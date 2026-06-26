<!-- VIGÍA Academic Documentation | Module: negation_handler.py | Hash: b8bde3c7 | Format: Standardized v1 -->

## ENGLISH

### What Is This Module?

`negation_handler.py` (VIGÍA hash `b8bde3c7`) is the deterministic lexical attenuation engine of the VIGÍA forensic pipeline. Its function is to prevent false-positive evidentiary signals caused by syntactic negation. When an upstream pattern matcher identifies a keyword or entity that is semantically nullified by a nearby negation operator ("not", "no", "never", etc.), a naive system would still count that match as evidence. This module prevents that error: it inspects a symmetric token window around every candidate match, and if a negation lexeme from the canonical corpus is found within that window, it applies a fixed multiplicative attenuation factor to the match confidence score.

Version 1.0, frozen at hash `b8bde3c7`, uses no machine-learning classifiers, no statistical inference engines, and no pseudo-random algorithms. Every execution with identical inputs and parameters produces bit-identical output. This reproducibility is a legal requirement, not an engineering preference: forensic testimony depends on tools that any independent examiner can re-run and verify.

The module deliberately does not resolve complex syntactic negation (double negation, anaphoric negation) to preserve determinism. This limitation is documented explicitly in the VIGÍA validation suite so it cannot be misrepresented during expert testimony.

### Key Concepts

| Concept | Definition |
|---------|-----------|
| Match tuple M_i | 4-tuple (s_i, e_i, c_i, τ_i): start index, end index, confidence score, pattern taxonomy identifier |
| Proximity window 𝒲 | Set of tokens at indices [max(0, s_i − δ), e_i + δ] around each match; δ is the configurable radius |
| Negation lexicon Σ_¬ | Authoritative set of negation operators loaded from lexical_corpus.py; Unicode-normalized, case-folded |
| Detection predicate 𝒟 | 1 if any λ_j ∈ Σ_¬ appears in 𝒲(M_i, δ); 0 otherwise |
| Attenuation operator 𝒜 | c′_i = c_i · α^𝒟; if 𝒟 = 0, confidence is unchanged; if 𝒟 = 1, confidence is multiplied by α ∈ (0,1) |
| Augmented record R′_i | Output tuple (M_i, c′_i, 𝒟, α, timestamp, execution_hash) transmitted downstream |
| O(n·w) complexity | Single-pass linear algorithm; n matches, w = 2δ + (e_i − s_i) tokens per window |
| Chain-of-custody trace | Cryptographic entry in audit_trail.py capturing input hash, parameter set P = (δ, α, Σ_¬ version), output hash |
| Daubert compliance | Known error rate = 0; only uncertainty source is empirical coverage of Σ_¬, which is bounded and version-controlled |

> **【Scientific Note】**
> Terms like "negation lexicon" and "detection predicate" may sound theoretical, but this module works exactly like a calibrated sensor with a threshold. The proximity window 𝒲 is the sensor's detection aperture. The negation lexicon Σ_¬ is the reference standard against which the sensor checks each reading. The attenuation factor α is the correction coefficient applied when the sensor detects an interfering signal. Peirce, Eco, and Grice provide the theoretical framework for *why* certain linguistic patterns reduce evidentiary weight — but the implementation is pure rule-based signal processing: no probability, no learning, no randomness. Every calibration parameter is fixed in the configuration manifest and locked by the module hash `b8bde3c7`. This is instrumentation, not interpretation.

### Glossary

| Term | Definition |
|------|-----------|
| negation_handler.py | Deterministic module that attenuates match confidence when negation is detected near a pattern match |
| lexical attenuation | Reduction of a confidence score by a fixed multiplicative factor when a negation signal is present |
| match event | A 4-tuple M_i representing one pattern detection: span coordinates, confidence, taxonomy type |
| proximity window | Token range [max(0, s_i−δ), e_i+δ] inspected for negation lexemes |
| negation lexicon | Canonical set Σ_¬ of negation operators maintained in lexical_corpus.py |
| attenuation factor α | Fixed coefficient ∈ (0,1) multiplied against confidence when negation is detected |
| lexical normalization | NFKD Unicode normalization + lowercasing + punctuation stripping applied to all tokens before comparison |
| augmented record R′_i | Output forensic record carrying original match plus modified confidence and audit metadata |
| chain of custody | Immutable cryptographic log in audit_trail.py recording every transformation with input/output hashes |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## ESPAÑOL

### ¿Qué es este módulo?

`negation_handler.py` (hash VIGÍA `b8bde3c7`) es el motor determinista de atenuación léxica del pipeline forense VIGÍA. Su función es prevenir señales de falso positivo causadas por la negación sintáctica. Cuando un matcher upstream identifica una entidad que, aunque presente en el texto, resulta semánticamente anulada por un operador de negación adyacente ("no", "never", "without", etc.), un sistema ingenuo contaría ese match como evidencia. Este módulo lo impide: inspecciona una ventana simétrica de tokens alrededor de cada match candidato y, si detecta un lexema de negación del corpus canónico dentro de esa ventana, aplica un factor multiplicativo fijo de atenuación al puntaje de confianza.

La versión 1.0, congelada en el hash `b8bde3c7`, no usa clasificadores de aprendizaje automático, motores de inferencia estadística ni algoritmos pseudoaleatorios. Cada ejecución con entradas y parámetros idénticos produce una salida bit a bit idéntica. Esta reproducibilidad no es una preferencia de ingeniería, sino un requisito legal: el testimonio forense depende de herramientas que cualquier perito independiente pueda re-ejecutar y verificar.

El módulo no resuelve deliberadamente la negación sintáctica compleja (doble negación, negación anafórica) para preservar el determinismo. Esta limitación está documentada explícitamente en el validation suite de VIGÍA.

### Conceptos clave

| Concepto | Definición |
|---------|-----------|
| Tupla de match M_i | 4-tupla (s_i, e_i, c_i, τ_i): índice inicial, índice final, puntaje de confianza, identificador taxonómico |
| Ventana de proximidad 𝒲 | Conjunto de tokens en índices [max(0, s_i − δ), e_i + δ] alrededor de cada match; δ es el radio configurable |
| Léxico de negación Σ_¬ | Conjunto autoritativo de operadores de negación cargado desde lexical_corpus.py; normalizado en Unicode |
| Predicado de detección 𝒟 | 1 si algún λ_j ∈ Σ_¬ aparece en 𝒲(M_i, δ); 0 en caso contrario |
| Operador de atenuación 𝒜 | c′_i = c_i · α^𝒟; si 𝒟 = 0, la confianza no cambia; si 𝒟 = 1, se multiplica por α ∈ (0,1) |
| Registro aumentado R′_i | Tupla de salida (M_i, c′_i, 𝒟, α, timestamp, execution_hash) transmitida downstream |
| Complejidad O(n·w) | Algoritmo lineal de pasada única; n matches, w = 2δ + (e_i − s_i) tokens por ventana |
| Traza de cadena de custodia | Entrada criptográfica en audit_trail.py con hash de entrada, parámetros P = (δ, α, versión de Σ_¬), hash de salida |
| Conformidad Daubert | Tasa de error = 0; única fuente de incertidumbre es la cobertura empírica de Σ_¬, acotada y versionada |

> **【Nota Científica】**
> Términos como "léxico de negación" y "predicado de detección" suenan teóricos, pero este módulo funciona exactamente como un sensor calibrado con umbral. La ventana de proximidad 𝒲 es la apertura de detección del sensor. El léxico Σ_¬ es el estándar de referencia contra el que el sensor compara cada lectura. El factor α es el coeficiente de corrección que se aplica cuando el sensor detecta una señal interferente. Peirce, Eco y Grice proveen el marco teórico para entender *por qué* ciertos patrones lingüísticos reducen el peso probatorio — pero la implementación es procesamiento de señales basado en reglas: sin probabilidad, sin aprendizaje, sin aleatoriedad. Cada parámetro de calibración está fijado en el manifiesto de configuración y bloqueado por el hash `b8bde3c7`. Esto es instrumentación, no interpretación.

### Glosario

| Término | Definición |
|--------|-----------|
| negation_handler.py | Módulo determinista que atenúa la confianza de un match cuando se detecta negación cercana |
| atenuación léxica | Reducción del puntaje de confianza por un factor multiplicativo fijo cuando hay señal de negación |
| evento de match | Tupla M_i representando una detección de patrón: coordenadas de span, confianza, tipo taxonómico |
| ventana de proximidad | Rango de tokens [max(0, s_i−δ), e_i+δ] inspeccionado en busca de lexemas de negación |
| léxico de negación | Conjunto canónico Σ_¬ de operadores de negación mantenido en lexical_corpus.py |
| factor de atenuación α | Coeficiente fijo ∈ (0,1) que se multiplica por la confianza cuando se detecta negación |
| normalización léxica | Normalización Unicode NFKD + conversión a minúsculas + eliminación de puntuación |
| registro aumentado R′_i | Registro forense de salida con match original, confianza modificada y metadatos de auditoría |
| cadena de custodia | Registro criptográfico inmutable en audit_trail.py de cada transformación con hashes de entrada y salida |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что представляет собой этот модуль?

`negation_handler.py` (хеш VIGÍA `b8bde3c7`) — детерминистский лексический фильтр-аттенюатор судебного конвейера VIGÍA. Его назначение — предотвращать ложноположительные доказательственные сигналы, вызванные синтаксическим отрицанием. Если вышестоящий модуль сопоставления шаблонов обнаруживает сущность, которая семантически аннулируется соседним оператором отрицания ("not", "no", "never" и др.), наивная система всё равно засчитает это совпадение как доказательство. Данный модуль пресекает такую ошибку: он проверяет симметричное окно токенов вокруг каждого кандидатного совпадения и, если в этом окне обнаруживается лексема из канонического словаря отрицания, применяет фиксированный мультипликативный коэффициент ослабления к оценке достоверности.

Версия 1.0, зафиксированная по хешу `b8bde3c7`, не использует классификаторы машинного обучения, статистические механизмы вывода и псевдослучайные алгоритмы. Каждый запуск с идентичными входными данными и параметрами порождает побитово идентичный результат. Это воспроизводимость не как инженерное предпочтение, а как правовое требование: судебное свидетельствование зависит от инструментов, которые любой независимый эксперт может перезапустить и верифицировать.

Модуль намеренно не разрешает сложные синтаксические конструкции отрицания (двойное отрицание, анафорическое отрицание) во имя сохранения детерминизма. Это ограничение явно задокументировано в валидационном наборе VIGÍA.

### Ключевые понятия

| Понятие | Определение |
|---------|------------|
| Кортеж совпадения M_i | 4-кортеж (s_i, e_i, c_i, τ_i): начальный индекс, конечный индекс, оценка достоверности, таксономический идентификатор |
| Окно близости 𝒲 | Множество токенов с индексами [max(0, s_i − δ), e_i + δ]; δ — настраиваемый радиус |
| Словарь отрицания Σ_¬ | Авторитетный набор операторов отрицания из lexical_corpus.py; Unicode-нормализованный, в нижнем регистре |
| Предикат обнаружения 𝒟 | 1, если какой-либо λ_j ∈ Σ_¬ присутствует в 𝒲(M_i, δ); 0 — в противном случае |
| Оператор ослабления 𝒜 | c′_i = c_i · α^𝒟; при 𝒟 = 0 достоверность не изменяется; при 𝒟 = 1 умножается на α ∈ (0,1) |
| Дополненная запись R′_i | Выходной кортеж (M_i, c′_i, 𝒟, α, timestamp, execution_hash), передаваемый вниз по конвейеру |
| Сложность O(n·w) | Линейный однопроходный алгоритм; n совпадений, w = 2δ + (e_i − s_i) токенов на окно |
| Трассировка цепочки хранения | Криптографическая запись в audit_trail.py с хешем входных данных, параметрами P = (δ, α, версия Σ_¬), хешем выходных данных |
| Соответствие Daubert | Частота ошибок = 0; единственный источник неточности — эмпирическая полнота Σ_¬, которая ограничена и версионирована |

> **【Научное примечание】**
> Такие термины, как «словарь отрицания» и «предикат обнаружения», могут звучать абстрактно, но этот модуль работает точно так же, как калиброванный датчик с порогом срабатывания. Окно близости 𝒲 — это апертура обнаружения датчика. Словарь Σ_¬ — эталонный стандарт, по которому датчик проверяет каждое показание. Коэффициент α — поправочный коэффициент, применяемый при обнаружении помехи. Пирс, Эко и Грайс предоставляют теоретическую основу для понимания *того, почему* определённые лингвистические паттерны снижают доказательственный вес, — но реализация представляет собой чистую обработку сигналов на основе правил: без вероятности, без обучения, без случайности. Каждый параметр калибровки зафиксирован в конфигурационном манифесте и заблокирован хешем модуля `b8bde3c7`. Это инструментация, а не интерпретация.

### Глоссарий

| Термин | Определение |
|--------|------------|
| negation_handler.py | Детерминистский модуль, ослабляющий достоверность совпадения при обнаружении отрицания вблизи него |
| лексическое ослабление | Снижение оценки достоверности на фиксированный мультипликативный коэффициент при наличии сигнала отрицания |
| событие совпадения | Кортеж M_i, представляющий одно обнаружение паттерна: координаты диапазона, достоверность, таксономический тип |
| окно близости | Диапазон токенов [max(0, s_i−δ), e_i+δ], проверяемый на наличие лексем отрицания |
| словарь отрицания | Канонический набор Σ_¬ операторов отрицания в lexical_corpus.py |
| коэффициент ослабления α | Фиксированный коэффициент ∈ (0,1), умножаемый на достоверность при обнаружении отрицания |
| лексическая нормализация | NFKD-нормализация Unicode + приведение к нижнему регистру + удаление пунктуации |
| дополненная запись R′_i | Выходная судебная запись с исходным совпадением, изменённой достоверностью и аудиторскими метаданными |
| цепочка хранения | Неизменяемый криптографический журнал в audit_trail.py каждого преобразования с хешами входных и выходных данных |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 本模块是什么？

`negation_handler.py`（VIGÍA 哈希值 `b8bde3c7`）是 VIGÍA 取证流程中的确定性词汇衰减引擎。其职能是防止因句法否定引发的假阳性证据信号。当上游模式匹配器识别出一个实体或关键词，但该词在语义上已被相邻否定算子（"not"、"no"、"never" 等）取消时，朴素系统仍会将该匹配计为证据。本模块阻止这一错误：它检查每个候选匹配周围的对称词元窗口，若在窗口内检测到来自规范否定词库的词汇，则对匹配置信度施加固定的乘法衰减因子。

1.0 版（已以哈希 `b8bde3c7` 冻结）不使用机器学习分类器、统计推断引擎或伪随机算法。在相同输入和参数条件下，每次执行均产生比特级一致的输出。这种可复现性不是工程偏好，而是法律要求：法医证词依赖任何独立检验员都能重新运行并验证的工具。

为保持确定性，本模块有意不处理复杂的句法否定（双重否定、回指否定）。该局限性已在 VIGÍA 验证套件中明确记录。

### 关键概念

| 概念 | 定义 |
|------|------|
| 匹配元组 M_i | 四元组 (s_i, e_i, c_i, τ_i)：起始词元索引、终止词元索引、置信度评分、模式分类标识符 |
| 邻近窗口 𝒲 | 以每个匹配为中心、索引范围 [max(0, s_i − δ), e_i + δ] 内的词元集合；δ 为可配置半径 |
| 否定词库 Σ_¬ | 从 lexical_corpus.py 加载的权威否定算子集合；经 Unicode 规范化、大小写折叠 |
| 检测谓词 𝒟 | 若 𝒲(M_i, δ) 中存在任意 λ_j ∈ Σ_¬，则为 1；否则为 0 |
| 衰减算子 𝒜 | c′_i = c_i · α^𝒟；𝒟 = 0 时置信度不变；𝒟 = 1 时乘以 α ∈ (0,1) |
| 增强记录 R′_i | 向下游传输的输出元组 (M_i, c′_i, 𝒟, α, timestamp, execution_hash) |
| O(n·w) 复杂度 | 线性单遍算法；n 为匹配数，w = 2δ + (e_i − s_i) 为每窗口词元数 |
| 保管链追踪 | audit_trail.py 中捕获输入哈希、参数集 P = (δ, α, Σ_¬ 版本)、输出哈希的密码学条目 |
| 符合 Daubert 标准 | 错误率 = 0；唯一不确定性来源是 Σ_¬ 的经验覆盖度，该覆盖度有界且受版本控制 |

> **【科学说明】**
> "否定词库"和"检测谓词"等术语听起来抽象，但本模块的工作原理与带阈值的已校准传感器完全相同。邻近窗口 𝒲 是传感器的探测孔径。否定词库 Σ_¬ 是传感器用于比对每次读数的参考标准。衰减因子 α 是检测到干扰信号时施加的校正系数。皮尔斯、艾柯和格赖斯为理解*为何*某些语言模式会降低证据权重提供了理论框架——但其实现是纯粹基于规则的信号处理：无概率、无学习、无随机。每个校准参数均固定于配置清单中，并由模块哈希 `b8bde3c7` 锁定。这是仪器测量，不是主观解读。

### 术语表

| 术语 | 定义 |
|------|------|
| negation_handler.py | 确定性模块，在模式匹配附近检测到否定时衰减匹配置信度 |
| 词汇衰减 | 存在否定信号时以固定乘法因子降低置信度评分 |
| 匹配事件 | 四元组 M_i，表示一次模式检测：跨度坐标、置信度、分类标识 |
| 邻近窗口 | 检测否定词元的词元范围 [max(0, s_i−δ), e_i+δ] |
| 否定词库 | lexical_corpus.py 中维护的规范否定算子集合 Σ_¬ |
| 衰减因子 α | ∈ (0,1) 的固定系数，检测到否定时乘以置信度 |
| 词汇规范化 | NFKD Unicode 规范化 + 小写转换 + 标点符号剥离 |
| 增强记录 R′_i | 包含原始匹配、修正后置信度及审计元数据的输出取证记录 |
| 保管链 | audit_trail.py 中记录每次变换（含输入输出哈希）的不可变密码学日志 |

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
