---
doc_hash: b8bde3c7
module: unknown
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

**Module Designation and Integrity:** `negation_handler.py` (VIGÍA hash `b8bde3c7`)

**1. Module Purpose and Forensic Scope**
The `negation_handler.py` module functions as a deterministic lexical attenuation engine within the VIGÍA forensic processing pipeline. Its forensic purpose is to reduce epistemic uncertainty in pattern-match evidence caused by syntactic negation. In textual evidence analysis, an upstream pattern matcher may identify entities, keywords, or semantic patterns that, although lexically present, are semantically nullified or inverted by adjacent negation operators. Without contextual disambiguation, such matches constitute false-positive evidentiary signals that can compromise investigative accuracy and legal admissibility. This module addresses the problem by imposing a bounded, rule-based contextual scan: for every candidate match emitted by the recognition layer, the system inspects a symmetric token window for negation lexemes. If a lexeme from the canonical negation corpus is detected within the window, the module applies a fixed multiplicative attenuation factor to the match confidence score. Version 1.0 employs an intentionally minimalist and predictable logic architecture, eschewing machine-learning classifiers, statistical inference engines, and pseudo-random algorithms. This exclusion of stochastic elements guarantees that every execution with identical inputs and parameters yields bit-identical evidentiary output, thereby preserving the scientific reproducibility required for forensic testimony.

**2. Mathematical Foundations**
The formal operation of the module is defined over a tokenized evidence stream. Let a pattern match event be modeled as a 4-tuple:
M_i = (s_i, e_i, c_i, τ_i)
where s_i ∈ ℕ₀ is the start token index, e_i ∈ ℕ₀ is the end token index, c_i ∈ [0, 1] represents the confidence score assigned by the upstream matcher, and τ_i ∈ 𝒯 is the pattern taxonomy identifier drawn from the forensic type system.

The contextual proximity window 𝒲 is a function of the match coordinates and a configurable integer radius δ (where δ ≥ 1):
𝒲(M_i, δ) = { t_k | k ∈ [ max(0, s_i − δ), e_i + δ ] }
Here, t_k denotes the k-th token in the normalized evidence stream. The window is inclusive and bounded by the stream origin at zero.

Let Σ_¬ represent the authoritative negation lexicon loaded from the `lexical_corpus.py` module:
Σ_¬ = { λ₁, λ₂, ..., λ_n }
Each element λ_j is a Unicode-normalized, case-folded lexical string denoting a negation operator (e.g., "not", "no", "never", "without", "excluding").

The detection predicate 𝒟 evaluates to true when the intersection of the window and the lexicon is non-empty:
𝒟(𝒲(M_i, δ), Σ_¬) = 
  1, if ∃ λ_j ∈ Σ_¬ : λ_j ∈ 𝒲(M_i, δ)
  0, otherwise

The confidence attenuation operator 𝒜 is defined using a fixed coefficient α ∈ (0, 1):
c'_i = 𝒜(c_i, 𝒟) = c_i · α^{𝒟}
Consequently, if no negation lexeme is detected (𝒟 = 0), the exponent vanishes and the confidence remains unaltered: c'_i = c_i. If negation is present (𝒟 = 1), the confidence is attenuated to c'_i = c_i · α. This operator establishes a deterministic, monotonic devaluation of evidentiary weight under negation scope.

The module further imposes a strict lexical normalization function 𝒩 on all tokens:
𝒩(t) = unicode_normalize(NFKD, lowercase(t)) \ punctuation_set
ensuring that comparison between window tokens and Σ_¬ is invariant to case, diacritics, and terminal punctuation.

**3. Algorithmic Procedure**
The module executes a linear, single-pass algorithm with O(n · w) complexity, where n is the number of input matches and w is the token window width (w = 2δ + (e_i − s_i)):

Phase A — Ingestion: The module receives an ordered stream {M_i} from `pattern_matcher.py` via the VIGÍA internal message bus. Each tuple is validated for coordinate bounds and confidence normalization.

Phase B — Contextualization: For each M_i, the module queries `tokenizer.py` to retrieve the pre-computed normalized token array. The fixed radius δ is read from the immutable configuration manifest established at pipeline initialization.

Phase C — Lexical Intersection: The algorithm constructs the token set 𝒲(M_i, δ) and computes its intersection with Σ_¬. Because both sets are normalized by 𝒩, the comparison reduces to exact string matching, eliminating fuzzy or probabilistic similarity computations.

Phase D — Attenuation: Should the intersection yield a non-empty set, 𝒟 = 1 is asserted. The module retrieves the pre-calibrated attenuation factor α from the configuration registry and applies the attenuation operator 𝒜 to produce c'_i.

Phase E — Record Construction and Emission: An augmented forensic record R'_i is assembled:
R'_i = ( M_i, c'_i, 𝒟, α, timestamp, execution_hash )
This record is transmitted to `confidence_aggregator.py` for composite scoring and simultaneously persisted by `evidence_logger.py`. A cryptographic trace is written to `audit_trail.py` capturing the input match hash, the parameter set P = (δ, α, Σ_¬ version), and the output record hash.

**4. Input/Output Specifications**
*Input:*
- Stream: `vigia.forensic.MatchEvent` protobuf objects containing s_i, e_i, c_i, τ_i.
- Configuration: δ ∈ ℤ⁺ (default 5 tokens); α ∈ (0, 1) ⊂ ℝ (default 0.5000); Σ_¬ URI pointing to the active lexicon in `lexical_corpus.py`.
- Constraints: c_i must be clamped to [0.0000, 1.0000]; δ must not exceed the VIGÍA maximum look-ahead bound of 1024 tokens.

*Output:*
- Stream: `vigia.forensic.AttenuatedMatch` protobuf objects containing the original coordinates, modified confidence c'_i, negation flag 𝒟, applied α, and processing metadata.
- Audit: Immutable trace entries in `audit_trail.py` conforming to VIGÍA chain-of-custody schema v2.1.

**5. Deterministic Guarantees and Forensic Reliability**
The module adheres to a strict deterministic contract:
∀ I, ∀ P = (δ, α, Σ_¬), ∀ E₁, E₂ : 𝒩(I, P, E₁) ≡ 𝒩(I, P, E₂)
where I is the input match stream, P is the fixed parameter set, and E represents any compliant execution environment. The transformation function 𝒩 contains no stochastic branching, no PRNG calls, no learned weight matrices, and no temporal dependencies. Consequently, the algorithmic error rate is zero; the only source of inaccuracy is the empirical coverage of Σ_¬, which is bounded, documented, and version-controlled. This property satisfies the Daubert standard’s requirement for a "known or potential error rate" and the existence of operational standards. It further ensures compliance with GB/T 29360-2012 (General Methods for Electronic Data Forensic Science Examination), which mandates reproducible tool behavior, and aligns with MLPS 2.0 requirements for deterministic audit trails in controlled data-processing environments.

**6. Integration with Related VIGÍA Modules**
- `pattern_matcher.py`: The upstream originator of {M_i}; supplies initial span coordinates and raw confidence scores.
- `tokenizer.py`: Provides tokenization boundaries, NFKD normalization, and punctuation stripping required to align 𝒲 with Σ_¬.
- `lexical_corpus.py`: Maintains the version-locked negation lexicon Σ_¬; updates require cryptographic re-signing.
- `confidence_aggregator.py`: Downstream module that weights c'_i into aggregate evidentiary metrics.
- `evidence_logger.py`: Immutable storage layer enforcing write-once-read-many (WORM) semantics for R'_i.
- `audit_trail.py`: Cryptographic logger preserving chain-of-custody for every transformation event.

**7. Version Integrity and Limitations**
Version 1.0, identified by hash `b8bde3c7`, is frozen for forensic certification. The module deliberately does not resolve complex syntactic negation (e.g., double negation, anaphoric negation, or implicit denial) in order to preserve determinism; these limitations are explicitly documented in the VIGÍA validation suite to prevent misrepresentation during expert testimony.

## ESPAÑOL

**Designación del módulo e integridad:** `negation_handler.py` (hash de VIGÍA `b8bde3c7`)

**1. Finalidad del módulo y alcance forense**
El módulo `negation_handler.py` (hash `b8bde3c7`) actúa como un motor determinista de atenuación léxica dentro del pipeline forense VIGÍA. Su propósito de evidencia consiste en reducir la incertidumbre epistémica presente en los *matches* de patrones generados por los motores de reconocimiento upstream, específicamente cuando dichos patrones aparecen bajo el alcance sintáctico de una negación. En el análisis de evidencia textual, el *pattern matcher* puede identificar entidades o secuencias léxicas que, aunque presentes en la superficie del texto, resultan anuladas o invertidas semánticamente por operadores de negación adyacentes. Sin una desambiguación contextual, esos *matches* constituyen señales de falso positivo que comprometen la precisión investigativa y la admisibilidad jurídica. Este módulo resuelve el problema imponiendo un escaneo contextual acotado y basado en reglas: para cada coincidencia candidata emitida por la capa de reconocimiento, el sistema inspecciona una ventana simétrica de tokens en busca de lexemas de negación. Si se detecta un lexema perteneciente al corpus canónico de negación dentro de dicha ventana, el módulo aplica un factor multiplicativo fijo de atenuación sobre el puntaje de confianza del *match*. La versión 1.0 emplea una arquitectura de lógica intencionalmente minimalista y predecible, prescindiendo de clasificadores de aprendizaje automático, motores de inferencia estadística y algoritmos seudoaleatorios. Esta exclusión de elementos estocásticos garantiza que cada ejecución con entradas y parámetros idénticos produzca una salida probatoriamente idéntica, preservando así la replicabilidad científica que exige el testimonio forense.

**2. Fundamentos matemáticos**
La operación formal del módulo se define sobre un flujo de evidencia tokenizado. Modelamos un evento de coincidencia de patrón como una 4-tupla:
M_i = (s_i, e_i, c_i, τ_i)
donde s_i ∈ ℕ₀ es el índice de token inicial, e_i ∈ ℕ₀ el índice final, c_i ∈ [0, 1] el puntaje de confianza asignado por el *matcher* upstream, y τ_i ∈ 𝒯 el identificador taxonómico del patrón extraído del sistema de tipos forense.

La ventana de proximidad contextual 𝒲 es función de las coordenadas del *match* y de un radio entero configurable δ (con δ ≥ 1):
𝒲(M_i, δ) = { t_k | k ∈ [ máx(0, s_i − δ), e_i + δ ] }
Aquí, t_k representa el k-ésimo token del flujo normalizado. La ventana es inclusiva y acotada inferiormente por el origen del flujo en cero.

Sea Σ_¬ el léxico de negación autoritativo cargado desde el módulo `lexical_corpus.py`:
Σ_¬ = { λ₁, λ₂, ..., λ_n }
Cada elemento λ_j es una cadena léxica normalizada en Unicode, convertida a minúsculas, que denota un operador de negación (por ejemplo: «not», «no», «never», «without», «excluding»).

El predicado de detección 𝒟 se evalúa como verdadero cuando la intersección entre la ventana y el léxico no es vacía:
𝒟(𝒲(M_i, δ), Σ_¬) =
  1, si ∃ λ_j ∈ Σ_¬ : λ_j ∈ 𝒲(M_i, δ)
  0, en caso contrario

El operador de atenuación de confianza 𝒜 se define mediante un coeficiente fijo α ∈ (0, 1):
c'_i = 𝒜(c_i, 𝒟) = c_i · α^{𝒟}
En consecuencia, si no se detecta ningún lexema de negación (𝒟 = 0), el exponente se anula y la confianza permanece inalterada: c'_i = c_i. Si la negación está presente (𝒟 = 1), la confianza se atenúa a c'_i = c_i · α. Este operador establece una devaluación determinista y monótona del peso probatorio bajo el alcance de la negación.

El módulo impone, además, una función estricta de normalización léxica 𝒩 sobre todos los tokens:
𝒩(t) = unicode_normalize(NFKD, minúsculas(t)) \ conjunto_puntuación
garantizando así que la comparación entre los tokens de la ventana y Σ_¬ sea invariante respecto de mayúsculas, diacríticos y signos de puntuación terminales.

**3. Descripción algorítmica**
El módulo ejecuta un algoritmo lineal de pasada única con complejidad O(n · w), donde n es la cantidad de *matches* de entrada y w es el ancho de la ventana en tokens (w = 2δ + (e_i − s_i)):

Fase A — Ingesta: el módulo recibe un flujo ordenado {M_i} desde `pattern_matcher.py` a través del bus interno de mensajes VIGÍA. Cada tupla se valida respecto de los límites de coordenadas y la normalización de confianza.

Fase B — Contextualización: para cada M_i, el módulo consulta a `tokenizer.py` para obtener el arreglo de tokens normalizados previamente computado. El radio fijo δ se lee desde el manifiesto de configuración inmutable establecido durante la inicialización del *pipeline*.

Fase C — Intersección léxica: el algoritmo construye el conjunto de tokens 𝒲(M_i, δ) y computa su intersección con Σ_¬. Dado que ambos conjuntos están normalizados mediante 𝒩, la comparación se reduce a una coincidencia exacta de cadenas, eliminando computaciones de similitud difusa o probabilística.

Fase D — Atenuación: si la intersección arroja un conjunto no vacío, se aserta 𝒟 = 1. El módulo recupera el factor de atenuación pre-calibrado α desde el registro de configuración y aplica el operador 𝒜 para producir c'_i.

Fase E — Construcción y emisión del registro: se ensambla un registro forense aumentado R'_i:
R'_i = ( M_i, c'_i, 𝒟, α, timestamp, execution_hash )
Este registro se transmite a `confidence_aggregator.py` para el cómputo de puntajes compuestos y, simultáneamente, se persiste mediante `evidence_logger.py`. Si inspeccionás la traza criptográfica, observarás que el parámetro α y el flag 𝒟 quedan registrados de forma inmutable en `audit_trail.py`, capturando el hash del *match* de entrada, el conjunto de parámetros P = (δ, α, versión de Σ_¬) y el hash del registro de salida.

**4. Especificaciones de entrada y salida**
*Entrada:*
- Flujo: objetos protobuf `vigia.forensic.MatchEvent` que contienen s_i, e_i, c_i, τ_i.
- Configuración: δ ∈ ℤ⁺ (predeterminado: 5 tokens); α ∈ (0, 1) ⊂ ℝ (predeterminado: 0,5000); URI de Σ_¬ apuntando al léxico activo en `lexical_corpus.py`.
- Restricciones: c_i debe estar acotado a [0,0000; 1,0000]; δ no debe superar el límite máximo de *look-ahead* de VIGÍA, fijado en 1024 tokens. Antes de procesar un lote, debés verificar que los valores de entrada estén dentro de estos rangos; de lo contrario, el módulo abortará la transacción para preservar la integridad probatoria.

*Salida:*
- Flujo: objetos protobuf `vigia.forensic.AttenuatedMatch` que contienen las coordenadas originales, la confianza modificada c'_i, el flag de negación 𝒟, el α aplicado y los metadatos de procesamiento.
- Auditoría: entradas inmutables en `audit_trail.py` conformes al esquema de cadena de custodia VIGÍA v2.1.

**5. Garantías deterministas y confiabilidad forense**
El módulo se adhiere a un contrato determinista estricto:
∀ I, ∀ P = (δ, α, Σ_¬), ∀ E₁, E₂ : 𝒩(I, P, E₁) ≡ 𝒩(I, P, E₂)
donde I es el flujo de *matches* de entrada, P es el conjunto fijo de parámetros y E representa cualquier entorno de ejecución conforme. La función de transformación 𝒩 no contiene bifurcaciones estocásticas, invocaciones a generadores seudoaleatorios, matrices de pesos aprendidos ni dependencias temporales. En consecuencia, la tasa de error algorítmica es cero; la única fuente de inexactitud radica en la cobertura empírica de Σ_¬, la cual está acotada, documentada y controlada por versionado. Si replicás la ejecución en un entorno conforme distinto, obtendrás un resultado bit-idéntico, lo cual respalda la admisibilidad bajo el estándar Daubert de una «tasa de error conocida o potencial» y de la existencia de estándares operativos. Asimismo, asegura el cumplimiento de la norma GB/T 29360-2012 (*General Methods for Electronic Data Forensic Science Examination*), que exige comportamiento reproducible de la herramienta, y se alinea con los requerimientos de MLPS 2.0 respecto de trazas de auditoría deterministas en entornos de procesamiento de datos controlados.

**6. Integración con módulos VIGÍA relacionados**
- `pattern_matcher.py`: originador upstream de {M_i}; provee las coordenadas de *span* y los puntajes de confianza originales.
- `tokenizer.py`: suministra los límites de tokenización, la normalización NFKD y la eliminación de puntuación necesarias para alinear 𝒲 con Σ_¬.
- `lexical_corpus.py`: mantiene el léxico de negación Σ_¬ bajo control de versiones criptográfico; toda actualización exige una firma de re-certificación.
- `confidence_aggregator.py`: módulo downstream que pondera c'_i dentro de métricas probatorias compuestas.
- `evidence_logger.py`: capa de almacenamiento inmutable que impone semántica WORM (*write-once-read-many*) sobre R'_i.
- `audit_trail.py`: logger criptográfico que preserva la cadena de custodia de cada evento de transformación.

**7. Integridad de versión y limitaciones**
La versión 1.0 (hash `b8bde3c7`) se encuentra congelada para certificación forense. El módulo resuelve deliberadamente la negación sintáctica superficial, prescindiendo de la negación compleja (por ejemplo, doble negación, negación anafórica o denegación implícita) a fin de preservar el determinismo; estas limitaciones están documentadas explícitamente en el *validation suite* de VIGÍA para evitar su tergiversación durante el testimonio de perito. Al operar el sistema, debés verificar que el hash del módulo coincida con `b8bde3c7` antes de admitir sus resultados en cadena de custodia.

## РУССКИЙ

**Обозначение модуля и контроль целостности:** `negation_handler.py` (хеш VIGÍA `b8bde3c7`)

**1. Назначение модуля и судебно-экспертный контекст**
Модуль `negation_handler.py` (хеш `b8bde3c7`) представляет собой детерминистский лексический фильтр-аттенюатор, функционирующий в составе судебного конвейера обработки данных VIGÍA. Его основное экспертное предназначение заключается в снижении эпистемологической неопределённости, возникающей при анализе текстовых доказательств вследствие синтаксического отрицания. В процессе текстовой экспертизы восходящий модуль сопоставления шаблонов может идентифицировать сущности или лексические последовательности, которые, будучи формально присутствующими в тексте, семантически аннулируются или инвертируются при помощи примыкающих операторов отрицания. При отсутствии контекстуальной дизъюнкции такие совпадения образуют ложноположительные доказательственные сигналы, способные скомпрометировать достоверность следственных выводов и допустимость материалов в судебном разбирательстве. Настоящий модуль устраняет указанную проблему путём введения ограниченного контекстного сканирования на основе формальных правил: для каждого кандидатного совпадения, выявленного распознающим уровнем, система исследует симметричное окно лексем на предмет наличия в нём элементов из канонического словаря отрицания. При обнаружении таковых модуль применяет фиксированный мультипликативный коэффициент ослабления к величине достоверности совпадения, формируя семантически скорректированный доказательственный показатель. Версия 1.0 намеренно использует минималистичную и предсказуемую логическую архитектуру, исключая классификаторы машинного обучения, статистические механизмы вывода и псевдослучайные алгоритмы. Отказ от стохастических элементов гарантирует, что каждый запуск при идентичных входных данных и параметрах порождает битово-идентичный выходной массив, обеспечивая тем самым научную воспроизводимость, необходимую для судебно-экспертного свидетельствования.

**2. Математические основания**
Формальная операция модуля определяется над токенизированным потоком доказательственных данных. Событие сопоставления шаблона моделируется как четвёрка:
M_i = (s_i, e_i, c_i, τ_i)
где s_i ∈ ℕ₀ — начальный токенный индекс, e_i ∈ ℕ₀ — конечный токенный индекс, c_i ∈ [0, 1] — оценка достоверности, присвоенная восходящим модулем сопоставления, а τ_i ∈ 𝒯 — идентификатор таксономии шаблона из судебной типологии.

Контекстное окно близости 𝒲 является функцией координат совпадения и настраиваемого целочисленного радиуса δ (при δ ≥ 1):
𝒲(M_i, δ) = { t_k | k ∈ [ max(0, s_i − δ), e_i + δ ] }
Здесь t_k обозначает k-й токен в нормализованном потоке данных. Окно является инклюзивным и ограниченным снизу нулевой точкой отсчёта потока.

Пусть Σ_¬ представляет авторитетный словарь лексем отрицания, загружаемый из модуля `lexical_corpus.py`:
Σ_¬ = { λ₁, λ₂, ..., λ_n }
Каждый элемент λ_j — это нормализованная в кодировке Unicode, приведённая к нижнему регистру лексическая строка, обозначающая оператор отрицания (например: «not», «no», «never», «without», «excluding»).

Предикат обнаружения 𝒟 принимает значение истина, когда пересечение окна и словаря непусто:
𝒟(𝒲(M_i, δ), Σ_¬) =
  1, если ∃ λ_j ∈ Σ_¬ : λ_j ∈ 𝒲(M_i, δ)
  0, в противном случае

Оператор ослабления достоверности 𝒜 определяется с использованием фиксированного коэффициента α ∈ (0, 1):
c'_i = 𝒜(c_i, 𝒟) = c_i · α^{𝒟}
Следовательно, при отсутствии лексем отрицания (𝒟 = 0) показатель степени обращается в нуль, и достоверность сохраняет неизменное значение: c'_i = c_i. При наличии отрицания (𝒟 = 1) достоверность ослабляется до величины c'_i = c_i · α. Данный оператор устанавливает детерминистское монотонное снижение доказательственного веса в области действия отрицания.

Модуль дополнительно вводит строгую функцию лексической нормализации 𝒩 для всех токенов:
𝒩(t) = unicode_normalize(NFKD, lowercase(t)) \ punctuation_set
что обеспечивает инвариантность сравнения токенов окна и элементов Σ_¬ относительно регистра, диакритических знаков и конечной пунктуации.

**3. Алгоритмическое описание**
Модуль выполняет линейный однопроходный алгоритм вычислительной сложности O(n · w), где n — количество входных совпадений, а w — ширина токенного окна (w = 2δ + (e_i − s_i)):

Фаза А — Ингрессия: модуль получает упорядоченный поток {M_i} от модуля `pattern_matcher.py` посредством внутренней шины сообщений VIGÍA. Каждый кортеж проходит валидацию координатных границ и нормализации достоверности.

Фаза Б — Контекстуализация: для каждого M_i модуль запрашивает у подсистемы `tokenizer.py` предварительно вычисленный нормализованный токенный массив. Фиксированный радиус δ считывается из неизменяемого конфигурационного манифеста, сформированного при инициализации конвейера.

Фаза В — Лексическое пересечение: алгоритм конструирует множество токенов 𝒲(M_i, δ) и вычисляет его пересечение со словарём Σ_¬. Поскольку оба множества нормализованы функцией 𝒩, сравнение сводится к точному строковому соответствию, исключая нечёткие или вероятностные вычисления сходства.

Фаза Г — Ослабление: если пересечение непусто, фиксируется 𝒟 = 1. Модуль извлекает предкалиброванный коэффициент ослабления α из конфигурационного реестра и применяет оператор 𝒜 для получения c'_i.

Фаза Д — Конструирование и эмиссия записи: формируется дополненная судебная запись R'_i:
R'_i = ( M_i, c'_i, 𝒟, α, timestamp, execution_hash )
Данная запись передаётся модулю `confidence_aggregator.py` для композитного оценивания и одновременно сохраняется подсистемой `evidence_logger.py`. Криптографическая трассировка записывается в `audit_trail.py` с фиксацией хеша входного совпадения, набора параметров P = (δ, α, версия Σ_¬) и хеша выходной записи.

**4. Спецификации входных и выходных данных**
*Входные данные:*
- Поток: объекты формата Protocol Buffers `vigia.forensic.MatchEvent`, содержащие s_i, e_i, c_i, τ_i.
- Конфигурация: δ ∈ ℤ⁺ (по умолчанию 5 токенов); α ∈ (0, 1) ⊂ ℝ (по умолчанию 0,5000); URI указателя на активный словарь Σ_¬ в модуле `lexical_corpus.py`.
- Ограничения: c_i должно быть ограничено диапазоном [0,0000; 1,0000]; δ не должен превышать максимальную границу опережающего просмотра VIGÍA, равную 1024 токенам.

*Выходные данные:*
- Поток: объекты формата Protocol Buffers `vigia.forensic.AttenuatedMatch`, содержащие исходные координаты, модифицированную достоверность c'_i, флаг отрицания 𝒟, применённый α и метаданные обработки.
- Аудит: неизменяемые записи трассировки в `audit_trail.py`, соответствующие схеме учёта цепочки хранения VIGÍA v2.1.

**5. Детерминистские гарантии и судебная надёжность**
Модуль придерживается строгого детерминистского контракта:
∀ I, ∀ P = (δ, α, Σ_¬), ∀ E₁, E₂ : 𝒩(I, P, E₁) ≡ 𝒩(I, P, E₂)
где I — входной поток совпадений, P — фиксированный набор параметров, E — любая совместимая среда исполнения. Преобразующая функция 𝒩 не содержит стохастических ветвлений, вызовов генераторов псевдослучайных чисел, обученных матриц весов и временных зависимостей. Вследствие этого алгоритмическая частота ошибок равна нулю; единственным источником неточности является эмпирическая полнота словаря Σ_¬, которая ограничена, документирована и контролируется версионированием. Указанное свойство удовлетворяет требованиям стандарта Daubert относительно «известной или потенциальной частоты ошибок» и наличия стандартов, регламентирующих эксплуатацию методики. Кроме того, оно обеспечивает соответствие стандарту GB/T 29360-2012 (общие методы судебной экспертизы электронных данных), предписывающему воспроизводимость поведения инструментов, и согласуется с требованиями MLPS 2.0 в отношении детерминистских трасс аудита в контролируемых средах обработки данных.

**6. Интеграция со смежными модулями VIGÍA**
- `pattern_matcher.py`: восходящий источник потока {M_i}; поставляет исходные координаты диапазона и первичные оценки достоверности.
- `tokenizer.py`: обеспечивает границы токенизации, нормализацию NFKD и удаление пунктуации, необходимые для сопоставления 𝒲 и Σ_¬.
- `lexical_corpus.py`: ведёт авторитетный словарь отрицания Σ_¬ с криптографическим контролем версий; обновление требует переподписывания.
- `confidence_aggregator.py`: нисходящий модуль, осуществляющий взвешивание c'_i в составе комплексных доказательственных метрик.
- `evidence_logger.py`: слой неизменяемого хранения, реализующий семантику WORM (write-once-read-many) для записей R'_i.
- `audit_trail.py`: криптографический журнал, сохраняющий цепочку хранения для каждого события преобразования.

**7. Целостность версии и ограничения**
Версия 1.0 (хеш `b8bde3c7`) заморожена для прохождения судебной сертификации. Модуль намеренно ограничивается разрешением поверхностного синтаксического отрицания, воздерживаясь от обработки сложных конструкций (двойное отрицание, анафорическое отрицание, имплицитное опровержение) с целью сохранения детерминизма; данные ограничения явно задокументированы в валидационном наборе VIGÍA для предотвращения искажений при даче экспертного заключения.

## 中文

**模块标识与完整性：** `negation_handler.py`（VIGÍA 哈希值 `b8bde3c7`）

**1. 模块目的与取证适用范围**
`negation_handler.py`（哈希 `b8bde3c7`）是 VIGÍA 取证处理流程中的确定性词汇衰减引擎。其取证目的在于降低因句法否定导致的模式匹配证据中的认识不确定性。在文本证据分析中，上游模式匹配器可能识别出实体或关键词序列，尽管其在文本表层存在，但会被相邻的否定算子在语义上取消或反转。若缺乏上下文消歧，此类匹配将构成假阳性证据信号，危及调查准确性与法律可采性。本模块通过实施有界、基于规则的上下文扫描来解决该问题：对于识别层发出的每一候选匹配，系统检查对称的词元窗口内是否存在否定词素。若在窗口内检测到来自规范否定词库的词汇，模块将对该匹配的置信度施加固定的乘法衰减因子，从而生成语义校正后的证据度量。1.0 版采用刻意简化的可预测逻辑架构，摒弃机器学习分类器、统计推断引擎及伪随机算法。排除随机性元素可确保在相同输入与参数条件下每次执行均产生比特级一致的证据输出，从而保障法医证词所要求的科学可复现性。

**2. 数学基础**
本模块的形式化运算建立在已分词的证据流之上。将模式匹配事件建模为四元组：
M_i = (s_i, e_i, c_i, τ_i)
其中 s_i ∈ ℕ₀ 为起始词元索引，e_i ∈ ℕ₀ 为结束词元索引，c_i ∈ [0, 1] 表示上游匹配器赋予的置信度评分，τ_i ∈ 𝒯 为取自取证类型系统的模式分类标识符。

上下文邻近窗口 𝒲 是匹配坐标与可配置整数半径 δ（δ ≥ 1）的函数：
𝒲(M_i, δ) = { t_k | k ∈ [ max(0, s_i − δ), e_i + δ ] }
此处 t_k 表示规范化证据流中的第 k 个词元。该窗口为闭区间，并在零起点处受下界约束。

令 Σ_¬ 表示从 `lexical_corpus.py` 模块加载的权威否定词库：
Σ_¬ = { λ₁, λ₂, ..., λ_n }
每个元素 λ_j 均为经 Unicode 规范化、大小写折叠后的词元字符串，表示否定算子（例如："not"、"no"、"never"、"without"、"excluding"）。

检测谓词 𝒟 在窗口与词库交集非空时判定为真：
𝒟(𝒲(M_i, δ), Σ_¬) =
  1，若 ∃ λ_j ∈ Σ_¬ : λ_j ∈ 𝒲(M_i, δ)
  0，否则

置信度衰减算子 𝒜 采用固定系数 α ∈ (0, 1) 定义：
c'_i = 𝒜(c_i, 𝒟) = c_i · α^{𝒟}
因此，若未检测到否定词元（𝒟 = 0），指数归零，置信度保持不变：c'_i = c_i。若存在否定（𝒟 = 1），置信度衰减为 c'_i = c_i · α。该算子确立了否定辖域内证据权重的确定性、单调性贬值。

此外，模块对所有词元实施严格的词汇规范化函数 𝒩：
𝒩(t) = unicode_normalize(NFKD, lowercase(t)) \ punctuation_set
确保窗口词元与 Σ_¬ 的比较不受大小写、变音符号及末尾标点的影响。

**3. 算法描述**
模块执行线性单遍算法，时间复杂度为 O(n · w)，其中 n 为输入匹配数量，w 为词元窗口宽度（w = 2δ + (e_i − s_i)）：

阶段 A — 摄取：模块通过 VIGÍA 内部消息总线从 `pattern_matcher.py` 接收有序流 {M_i}。对每个元组进行坐标边界与置信度归一化校验。

阶段 B — 上下文构建：对于每个 M_i，模块查询 `tokenizer.py` 以获取预计算的规范化词元数组。固定半径 δ 从流程初始化时建立的不可变配置清单中读取。

阶段 C — 词汇交集：算法构建词元集合 𝒲(M_i, δ) 并计算其与 Σ_¬ 的交集。由于两集合均经 𝒩 规范化，比较退化为精确字符串匹配，排除了模糊或概率相似性计算。

阶段 D — 衰减：若交集非空，则断言 𝒟 = 1。模块从配置注册表中提取预校准的衰减因子 α，并应用算子 𝒜 生成 c'_i。

阶段 E — 记录构建与输出：组装增强型取证记录 R'_i：
R'_i = ( M_i, c'_i, 𝒟, α, timestamp, execution_hash )
该记录被传送至下游的 `confidence_aggregator.py` 进行复合评分，同时由 `evidence_logger.py` 持久化存储。`audit_trail.py` 写入加密追踪条目，捕获输入匹配哈希、参数集 P = (δ, α, Σ_¬ 版本) 及输出记录哈希。

**4. 输入/输出规格**
*输入：*
- 数据流：包含 s_i、e_i、c_i、τ_i 的 Protocol Buffers 对象 `vigia.forensic.MatchEvent`。
- 配置参数：δ ∈ ℤ⁺（默认值：5 个词元）；α ∈ (0, 1) ⊂ ℝ（默认值：0.5000）；指向 `lexical_corpus.py` 中活跃词库 Σ_¬ 的 URI。
- 约束条件：c_i 必须钳位至 [0.0000, 1.0000]；δ 不得超过 VIGÍA 最大前视边界 1024 个词元。

*输出：*
- 数据流：包含原始坐标、修正后置信度 c'_i、否定标志 𝒟、所用 α 及处理元数据的 Protocol Buffers 对象 `vigia.forensic.AttenuatedMatch`。
- 审计：符合 VIGÍA 证据保管链模式 v2.1 的、写入 `audit_trail.py` 的不可变追踪条目。

**5. 确定性保证与取证可靠性**
模块遵循严格的确定性契约：
∀ I, ∀ P = (δ, α, Σ_¬), ∀ E₁, E₂ : 𝒩(I, P, E₁) ≡ 𝒩(I, P, E₂)
其中 I 为输入匹配流，P 为固定参数集，E 为任何兼容执行环境。变换函数 𝒩 不包含随机分支、伪随机数生成器调用、学习权重矩阵或时间依赖。因此，算法错误率为零；唯一不精确来源为 Σ_¬ 的经验覆盖度，该覆盖度有界、已记录并受版本控制。此特性满足 Daubert 标准关于"已知或潜在错误率"及"技术操作存在受控标准"的要求。同时，它确保符合 GB/T 29360-2012《电子数据法庭科学鉴定通用方法》对工具可复现行为的规定，并与 MLPS 2.0（网络安全等级保护制度 2.0）关于受控数据处理环境中确定性审计追踪的要求相一致。

**6. 与相关 VIGÍA 模块的关联**
- `pattern_matcher.py`：上游 {M_i} 来源；提供初始跨度坐标与原始置信度评分。
- `tokenizer.py`：提供分词边界、NFKD 规范化及标点剔除功能，以保障 𝒲 与 Σ_¬ 的对齐。
- `lexical_corpus.py`：维护经加密版本锁定的否定词库 Σ_¬；更新需重新签名认证。
- `confidence_aggregator.py`：下游模块，负责将 c'_i 加权纳入综合证据指标。
- `evidence_logger.py`：不可变存储层，对 R'_i 实施一次写入多次读取（WORM）语义。
- `audit_trail.py`：加密日志记录器，为每次变换事件保存证据保管链。

**7. 版本完整性与局限性**
1.0 版（哈希 `b8bde3c7`）已冻结以供取证认证。本模块有意仅解决表层句法否定，不处理复杂否定结构（如双重否定、回指否定或隐含否认），以维护确定性；上述局限性已在 VIGÍA 验证套件中明确记录，防止在专家作证过程中被误述。