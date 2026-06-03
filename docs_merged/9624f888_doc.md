<!--
VIGIA Academic Documentation
Module: 9624f888
Batch ID: vigia-doc-0148-9624f888
Generated: 2026-05-20T14:56:47.876354+00:00
-->

---

## ENGLISH

### What Is This Module?

The `adversarial_mutation_suite.py` module is a deterministic test-bench for forensic text pipelines. Its purpose is to generate perturbed versions of an original digital artifact (a plain text string) in order to verify whether downstream analytical tools remain robust. Rather than relying on physical hardware variations, the module treats the text as a signal and applies precisely catalogued symbolic disturbances. Every perturbation is reproducible: given the same input text and integer seed, the output mutation is identical. This reproducibility is achieved through deterministic integer arithmetic and cryptographic hashing (SHA-256), never through floating-point approximations.

The suite is organized around five core attack patterns (called GAPs—Generator Attack Patterns). Each pattern targets a specific class of algorithmic measurement: entropy calculators, complexity estimators (Lempel-Ziv, Permutation Entropy), or structural classifiers. The module also provides normalization functions that act as inverse filters, allowing an auditor to verify whether a given perturbation can be neutralized before analysis.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---------|-------------|-------------------|
| Deterministic Mutation | A text transform that produces the exact same output every time it receives the same inputs (text + integer seed). | Ensures experimental reproducibility; eliminates non-deterministic noise from the test procedure itself. |
| Entropy Inflation (GAP-01) | Injection of invisible or low-visibility Unicode control characters at exact integer positions. | Tests whether entropy estimators confuse formatting noise with information content. |
| Symbolic Explosion (GAP-02) | Replacement of characters with visual homoglyphs and alternating capitalization. | Expands the alphabet size without altering human readability, probing dictionary-based and indexing tools. |
| False Structure Induction (GAP-06) | Generation of text sharing the original's bigram frequency distribution but lacking semantic coherence. | Evaluates whether statistical classifiers mistake surface pattern for genuine linguistic structure. |
| Tie-Break Exploitation (GAP-09) | Forcing massive identical-value runs by replacing exact integer counts of characters with a single fill symbol. | Attacks Permutation Entropy, which requires strict ranking; ties collapse the rank spectrum. |
| LZ Period Aliasing (GAP-10) | Imposition of an exact periodic structure whose length is the integer square root of the text length. | Exploits the asymptotic normalization of LZ76 complexity on short integer sequences. |
| Forensic Normalization | Discrete symbolic filters (NFKC, casefold, confusable mapping, control stripping) that canonicalize text. | Provides a deterministic preprocessing layer so that downstream integer-based metrics operate on clean inputs. |

### Component Inventory

| Component | Role | Deterministic Guarantee |
|-----------|------|------------------------|
| `MutationResult` | Data container for the output of a single mutation. Stores the mutation identifier, original text reference, and perturbed text. | `mutation_id` is a SHA-256 digest computed from the concatenation of the mutator name and origin parameters using integer bit-string operations. |
| `NoiseInjectionMutator` | Executes GAP-01. Computes exact integer positions for noise insertion using modular arithmetic on the seed. | Number of injected symbols is an exact integer count derived from the length of the text and the rational rate parameter. |
| `SymbolExplosionMutator` | Executes GAP-02. Selects homoglyph substitutions from a finite confusable map. | Substitutions are indexed by integer offsets into a static lookup table. |
| `FalseStructureMutator` | Executes GAP-06. Reconstructs a bigram-compatible string via discrete Markov sampling. | State transitions are governed by integer frequency counts, not probabilities. |
| `TieBreakMutator` | Executes GAP-09. Replaces exactly `tie_fraction` of characters (as an integer count) with a `fill_value`. | The replacement count is calculated with integer division; no rounding error occurs. |
| `PeriodAliasingMutator` | Executes GAP-10. Repeats a base pattern of length √n (integer square root) to fill the text. | Period and repetition count are pure integer relations. |
| `AdversarialMutationSuite` | Orchestrator. Runs all mutators against an input text and assembles a structured report. | Iteration order and seed propagation are fixed by integer sequence logic. |

### Glossary

| Term | Definition |
|------|------------|
| **Adversarial Vector** | A deliberately perturbed version of an input artifact designed to trigger a specific failure mode in an analytical tool. |
| **Bigram** | A pair of adjacent symbols. In this module, bigram frequencies are counted as exact integers. |
| **Canonical Equivalence** | The property that two different Unicode strings represent the same abstract character sequence. The NFKC normalization form resolves this deterministically. |
| **Confusable Character** | A Unicode symbol that is visually indistinguishable from another (e.g., Latin "A" vs. Cyrillic "А"). The module maps these via a finite, static table. |
| **Control Strip** | Removal of non-printing Unicode categories (formatting controls, zero-width joiners) to produce a visible-only symbol stream. |
| **Deterministic Seed** | An integer value that initializes a pseudo-random number generator so that its output sequence is identical across every execution. |
| **Homoglyph** | A subclass of confusable characters that share identical or near-identical glyphs. |
| **Integer Square Root** | The largest integer not exceeding the exact square root of a number (e.g., isqrt(10) = 3). Used to fix the period length in GAP-10. |
| **LZ76 Complexity** | A measure of symbolic complexity defined by the count of distinct patterns in a sequence, normalized by an asymptotic integer factor n / log₂(n). |
| **Permutation Entropy** | An algorithm that measures disorder by comparing the ranks of consecutive values in a sliding window. Requires a total ordering; ties break that ordering. |
| **SHA-256** | A cryptographic hash function that produces a 256-bit integer digest. Here it serves as a deterministic fingerprint for mutation provenance. |
| **Unicode Category** | A classification assigned to each Unicode codepoint (e.g., letter, number, format, control). The module uses these categories for deterministic stripping. |

### 【Scientific Note】Semiotic Terminology Is Sensor Engineering, Not Mysticism

The documentation and internal nomenclature of the VIGÍA project occasionally draw on the semiotic frameworks of **Charles Sanders Peirce** (sign–object–interpretant triads), **Umberto Eco** (confusable signs and semantic noise), and **Paul Grice** (cooperative maxims and implicature). This is not an appeal to literary mysticism; it is a rigorous engineering analogy.

Think of a text as a signal measured by a scientific instrument (the forensic pipeline). Peirce’s triad describes how the instrument parses the signal: the raw voltage is the *sign*, the physical phenomenon is the *object*, and the calibrated reading is the *interpretant*. Eco’s confusable signs are indistinguishable sensor readings—two different physical states that produce identical voltages, creating aliasing. Grice’s maxims are the communication protocol: if the transmitter and receiver share a protocol (cooperative principle), then inserting a message that follows the protocol’s grammar but violates its semantics is equivalent to injecting deterministic interference—a false structure that the sensor’s firmware misclassifies as valid data.

Therefore, when this module induces "false structure" or injects "symbolic noise," it is performing semiotic engineering: the deliberate corruption of a communication protocol to test the fault tolerance of the receiver. The mathematics remain strictly deterministic integer arithmetic throughout.

---

Now ESPAÑOL. Need to mirror content but in Spanish.

Key terms:
- Deterministic Mutation -> Mutación Determinista
- Entropy Inflation -> Inflación de Entropía
- Symbolic Explosion -> Explosión Simbólica
- False Structure -> Estructura Falsa
- Tie-Break -> Ruptura de Empates / Explotación de Empates
- LZ Period Aliasing -> Aliasing de Período LZ
- Forensic Normalization -> Normalización Forense
- Component Inventory -> Inventario de Componentes
- Glossary -> Glosario
- Scientific Note -> Nota Científica
- Peirce, Eco, Grice remain Peirce, Eco, Grice.

Sensor analogy: "texto como señal medida por un instrumento científico"

---

## ESPAÑOL

### ¿Qué es este módulo?

El módulo `adversarial_mutation_suite.py` es un banco de pruebas determinista para pipelines forenses de texto. Su propósito es generar versiones perturbadas de un artefacto digital original (una cadena de texto plano) para verificar si las herramientas analíticas downstream permanecen robustas. En lugar de depender de variaciones de hardware físico, el módulo trata el texto como una señal y aplica disturbios simbólicos precisamente catalogados. Cada perturbación es reproducible: dado el mismo texto de entrada y una semilla entera, la mutación de salida es idéntica. Esta reproducibilidad se logra mediante aritmética entera determinista y hash criptográfico (SHA-256), nunca a través de aproximaciones de punto flotante.

El conjunto se organiza alrededor de cinco patrones de ataque centrales (llamados GAPs—Generator Attack Patterns). Cada patrón apunta a una clase específica de medición algorítmica: calculadoras de entropía, estimadores de complejidad (Lempel-Ziv, Entropía de Permutación) o clasificadores estructurales. El módulo también provee funciones de normalización que actúan como filtros inversos, permitiendo a un auditor verificar si una perturbación dada puede ser neutralizada antes del análisis.

### Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|----------|-------------|----------------------|
| Mutación Determinista | Transformación de texto que produce exactamente la misma salida cada vez que recibe las mismas entradas (texto + semilla entera). | Garantiza la reproducibilidad experimental; elimina el ruido no determinista del propio procedimiento de prueba. |
| Inflación de Entropía (GAP-01) | Inyección de caracteres de control Unicode invisibles o de baja visibilidad en posiciones enteras exactas. | Comprueba si los estimadores de entropía confunden el ruido de formato con contenido informativo. |
| Explosión Simbólica (GAP-02) | Reemplazo de caracteres por homoglifos visuales y alternancia de capitalización. | Expande el tamaño del alfabeto sin alterar la legibilidad humana, sondeando herramientas basadas en diccionario e indexación. |
| Inducción de Estructura Falsa (GAP-06) | Generación de texto que comparte la distribución de frecuencias bigrama del original pero carece de coherencia semántica. | Evalúa si los clasificadores estadísticos confunden el patrón superficial con estructura lingüística genuina. |
| Explotación de Empates (GAP-09) | Forzamiento de secuencias masivas de valores idénticos reemplazando conteos exactos enteros de caracteres por un símbolo de relleno único. | Ataca la Entropía de Permutación, que requiere ordenamiento estricto; los empates colapsan el espectro de rangos. |
| Aliasing de Período LZ (GAP-10) | Imposición de una estructura periódica exacta cuya longitud es la raíz cuadrada entera de la longitud del texto. | Explota la normalización asintótica de la complejidad LZ76 en secuencias enteras cortas. |
| Normalización Forense | Filtros simbólicos discretos (NFKC, casefold, mapeo de confusibles, eliminación de controles) que canonizan el texto. | Provee una capa de preprocesamiento determinista para que las métricas basadas en enteros downstream operen sobre entradas limpias. |

### Inventario de Componentes

| Componente | Rol | Garantía Determinista |
|------------|-----|----------------------|
| `MutationResult` | Contenedor de datos para la salida de una mutación individual. Almacena el identificador de mutación, referencia al texto original y texto perturbado. | `mutation_id` es un resumen SHA-256 calculado a partir de la concatenación del nombre del mutador y parámetros de origen usando operaciones de bit-string enteras. |
| `NoiseInjectionMutator` | Ejecuta GAP-01. Calcula posiciones enteras exactas para inserción de ruido usando aritmética modular sobre la semilla. | El número de símbolos inyectados es un conteo entero exacto derivado de la longitud del texto y el parámetro de tasa racional. |
| `SymbolExplosionMutator` | Ejecuta GAP-02. Selecciona sustituciones por homoglifos desde un mapa de confusibles finito. | Las sustituciones se indexan por desplazamientos enteros en una tabla de búsqueda estática. |
| `FalseStructureMutator` | Ejecuta GAP-06. Reconstruye una cadena compatible de bigramas mediante muestreo de Markov discreto. | Las transiciones de estado se gobiernan por conteos de frecuencia enteros, no probabilidades. |
| `TieBreakMutator` | Ejecuta GAP-09. Reemplaza exactamente `tie_fraction` de caracteres (como conteo entero) con un `fill_value`. | El conteo de reemplazo se calcula con división entera; no ocurre error de redondeo. |
| `PeriodAliasingMutator` | Ejecuta GAP-10. Repite un patrón base de longitud √n (raíz cuadrada entera) para llenar el texto. | El período y el conteo de repeticiones son relaciones puramente enteras. |
| `AdversarialMutationSuite` | Orquestador. Ejecuta todos los mutadores sobre un texto de entrada y ensambla un reporte estructurado. | El orden de iteración y la propagación de semillas están fijados por lógica de secuencia entera. |

### Glosario

| Término | Definición |
|---------|------------|
| **Vector Adversarial** | Versión deliberadamente perturbada de un artefacto de entrada diseñada para disparar un modo específico de falla en una herramienta analítica. |
| **Bigrama** | Par de símbolos adyacentes. En este módulo, las frecuencias bigrama se cuentan como enteros exactos. |
| **Equivalencia Canónica** | Propiedad por la cual dos cadenas Unicode distintas representan la misma secuencia de caracteres abstractos. La forma de normalización NFKC resuelve esto de manera determinista. |
| **Carácter Confusible** | Símbolo Unicode visualmente indistinguible de otro (p. ej., "A" latina vs. "А" cirílica). El módulo los mapea mediante una tabla finita y estática. |
| **Eliminación de Controles** | Remoción de categorías Unicode no imprimibles (controles de formato, ensanchadores de ancho cero) para producir un flujo de símbolos únicamente visibles. |
| **Semilla Determinista** | Valor entero que inicializa un generador de números pseudoaleatorios de modo que su secuencia de salida sea idéntica en cada ejecución. |
| **Homoglifo** | Subclase de caracteres confusibles que comparten glifos idénticos o casi idénticos. |
| **Raíz Cuadrada Entera** | El entero más grande que no excede la raíz cuadrada exacta de un número (p. ej., isqrt(10) = 3). Se usa para fijar la longitud del período en GAP-10. |
| **Complejidad LZ76** | Medida de complejidad simbólica definida por el conteo de patrones distintos en una secuencia, normalizada por un factor entero asintótico n / log₂(n). |
| **Entropía de Permutación** | Algoritmo que mide el desorden comparando los rangos de valores consecutivos en una ventana deslizante. Requiere orden total; los empates rompen ese ordenamiento. |
| **SHA-256** | Función hash criptográfica que produce un resumen entero de 256 bits. Aquí sirve como huella determinista para la proveniencia de la mutación. |
| **Categoría Unicode** | Clasificación asignada a cada punto de código Unicode (p. ej., letra, número, formato, control). El módulo usa estas categorías para la eliminación determinista. |

### 【Nota Científica】La Terminología Semiótica es Ingeniería de Sensores, no Misticismo

La documentación y la nomenclatura interna del proyecto VIGÍA ocasionalmente recurren a los marcos semióticos de **Charles Sanders Peirce** (tríadas signo–objeto–interpretante), **Umberto Eco** (signos confusibles y ruido semántico) y **Paul Grice** (máximas cooperativas e implicaturas). Esto no es un apelo al misticismo literario; es una analogía de ingeniería rigurosa.

Piense en un texto como una señal medida por un instrumento científico (el pipeline forense). La tríada de Peirce describe cómo el instrumento analiza la señal: el voltaje crudo es el *signo*, el fenómeno físico es el *objeto*, y la lectura calibrada es el *interpretante*. Los signos confusibles de Eco son lecturas de sensor indistinguibles: dos estados físicos distintos que producen voltajes idénticos, creando aliasing. Las máximas de Grice son el protocolo de comunicación: si el transmisor y el receptor comparten un protocolo (principio cooperativo), entonces insertar un mensaje que sigue la gramática del protocolo pero viola su semántica es equivalente a inyectar interferencia determinista: una estructura falsa que el firmware del sensor clasifica erróneamente como datos válidos.

Por lo tanto, cuando este módulo induce "estructura falsa" o inyecta "ruido simbólico", está realizando ingeniería semiótica: la corrupción deliberada de un protocolo de comunicación para probar la tolerancia a fallas del receptor. Las matemáticas permanecen estrictamente como aritmética entera determinista de principio a fin.

---

Now РУССКИЙ.

Key terms:
- Deterministic Mutation -> Детерминированная мутация
- Entropy Inflation -> Инфляция энтропии
- Symbolic Explosion -> Символический взрыв / Эксплозия символов
- False Structure -> Ложная структура
- Tie-Break -> Эксплуатация ничейных ситуаций / Разрешение ничьих
- LZ Period Aliasing -> Алиасинг периода LZ
- Forensic Normalization -> Криминалистическая нормализация
- Component Inventory -> Перечень компонентов
- Glossary -> Глоссарий
- Scientific Note -> Научное примечание
- Sensor analogy: "текст как сигнал, измеряемый научным прибором"

Note on Peirce/Eco/Grice: Пирс, Эко, Грайс.

Terms:
- text artifact -> текстовый артефакт
- downstream -> ниже по потоку / последующие этапы
- integer arithmetic -> целочисленная арифметика
- floating-point -> с плавающей точкой (but avoid using it as explanation; mention deterministic integer instead)
- rate parameter -> параметр частоты / параметр скорости внесения (but integer count based)
- seed -> начальное значение / зерно
- mutation_id -> идентификатор мутации

---

## РУССКИЙ

### Что представляет собой этот модуль?

Модуль `adversarial_mutation_suite.py` — это детерминированный испытательный стенд для криминалистических текстовых конвейеров. Его назначение — генерировать возмущённые версии исходного цифрового артефакта (строки простого текста) с целью проверки устойчивости последующих аналитических инструментов. Вместо того чтобы полагаться на физические вариации оборудования, модуль рассматривает текст как сигнал и применяет точно каталогизированные символические возмущения. Каждое возмущение воспроизводимо: при одинаковых входных данных (текст + целочисленное начальное значение) результат мутации идентичен. Эта воспроизводимость достигается детерминированной целочисленной арифметикой и криптографическим хешированием (SHA-256), но никогда — приближениями с плавающей точкой.

Набор построен вокруг пяти базовых шаблонов атак (GAP — Generator Attack Patterns). Каждый шаблон нацелен на определённый класс алгоритмических измерений: калькуляторы энтропии, оценщики сложности (Лемпел–Зив, перестановочная энтропия) или структурные классификаторы. Модуль также предоставляет функции нормализации, действующие как обратные фильтры, позволяя аудитору проверить, может ли конкретное возмущение быть нейтрализовано до анализа.

### Ключевые концепции

| Концепция | Описание | Научное значение |
|-----------|----------|------------------|
| Детерминированная мутация | Преобразование текста, дающее точно такой же результат при каждом запуске с одинаковыми входными данными (текст + целочисленное начальное значение). | Гарантирует экспериментальную воспроизводимость; исключает недетерминированный шум из самой процедуры тестирования. |
| Инфляция энтропии (GAP-01) | Внедрение невидимых или слабовидимых управляющих символов Unicode в точно определённые целочисленные позиции. | Проверяет, не принимают ли оценщики энтропии форматирующий шум за информационное содержание. |
| Символический взрыв (GAP-02) | Замена символов визуальными омоглифами и чередование регистра. | Расширяет размер алфавита без изменения человекочитаемости, исследуя словарные и индексные инструменты. |
| Индукция ложной структуры (GAP-06) | Генерация текста, разделяющего с исходным частотное распределение биграмм, но лишённого семантической когерентности. | Оценивает, не принимают ли статистические классификаторы поверхностный паттерн за подлинную лингвистическую структуру. |
| Эксплуатация ничейных ситуаций (GAP-09) | Принудительное создание длинных последовательностей одинаковых значений путём замены точного целочисленного количества символов одним заполнителем. | Атакует перестановочную энтропию, требующую строгого ранжирования; ничьи сворачивают спектр рангов. |
| Алиасинг периода LZ (GAP-10) | Наложение точной периодической структуры, длина которой равна целочисленному квадратному корню из длины текста. | Эксплуатирует асимптотическую нормализацию сложности LZ76 на коротких целочисленных последовательностях. |
| Криминалистическая нормализация | Дискретные символические фильтры (NFKC, приведение регистра, маппинг омоглифов, удаление управляющих символов), канонизирующие текст. | Обеспечивает детерминированный слой предобработки, чтобы последующие целочисленные метрики работали с очищенными входными данными. |

### Перечень компонентов

| Компонент | Роль | Детерминированная гарантия |
|-----------|------|---------------------------|
| `MutationResult` | Контейнер данных для результата отдельной мутации. Хранит идентификатор мутации, ссылку на исходный текст и возмущённый текст. | `mutation_id` — дайджест SHA-256, вычисленный от конкатенации имени мутатора и параметров происхождения с помощью операций над целочисленными битовыми строками. |
| `NoiseInjectionMutator` | Выполняет GAP-01. Вычисляет точные целочисленные позиции для вставки шума с помощью модульной арифметики на основе начального значения. | Число внедряемых символов — точное целое, полученное из длины текста и рационального параметра частоты. |
| `SymbolExplosionMutator` | Выполняет GAP-02. Выбирает замены омоглифами из конечной таблицы конфузабельных символов. | Замены индексируются целочисленными смещениями в статической таблице поиска. |
| `FalseStructureMutator` | Выполняет GAP-06. Реконструирует строку, совместимую с биграммами, дискретной выборкой Маркова. | Переходы состояний управляются целочисленными частотными счётчиками, а не вероятностями. |
| `TieBreakMutator` | Выполняет GAP-09. Заменяет ровно `tie_fraction` символов (как целое количество) на `fill_value`. | Количество замен вычисляется целочисленным делением; ошибок округления не возникает. |
| `PeriodAliasingMutator` | Выполняет GAP-10. Повторяет базовый шаблон длины √n (целочисленный квадратный корень) до заполнения текста. | Период и количество повторений — чисто целочисленные соотношения. |
| `AdversarialMutationSuite` | Оркестратор. Запускает все мутаторы на входном тексте и формирует структурированный отчёт. | Порядок итераций и распространение начального значения фиксированы целочисленной логикой последовательности. |

### Глоссарий

| Термин | Определение |
|--------|-------------|
| **Адверсарный вектор** | Преднамеренно возмущённая версия входного артефакта, предназначенная для вызова конкретного режима отказа аналитического инструмента. |
| **Биграмма** | Пара смежных символов. В данном модуле частоты биграмм подсчитываются как точные целые числа. |
| **Каноническая эквивалентность** | Свойство, при котором две различные строки Unicode представляют одну и ту же абстрактную последовательность символов. Форма нормализации NFKC разрешает её детерминированно. |
| **Конфузабельный символ** | Символ Unicode, визуально неотличимый от другого (например, латинская «A» и кириллическая «А»). Модуль отображает их через конечную статическую таблицу. |
| **Удаление управляющих символов** | Устранение непечатаемых категорий Unicode (форматирующие управляющие символы, соединители нулевой ширины) для получения потока исключительно видимых символов. |
| **Детерминированное начальное значение** | Целое число, инициализирующее генератор псевдослучайных чисел так, что
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
