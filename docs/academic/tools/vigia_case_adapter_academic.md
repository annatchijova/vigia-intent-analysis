## ENGLISH

The `vigia/tools/vigia_case_adapter.py` module constitutes a critical deterministic mediation layer within the VIGÍA forensic analysis framework, specifically engineered to normalize, ensemble, and adapt per-artifact statistical scores into case-admissible evidentiary metrics. Version 6 of this module implements the *Opcion B Weighted Domain Ensemble* algorithm, a mathematically exact scoring methodology designed to satisfy reproducibility mandates under the Daubert standard for scientific testimony, while simultaneously conforming to GB/T digital forensic national standards and MLPS 2.0 data-processing security requirements. Operating as the evidentiary gateway between low-level artifact extraction and high-level case synthesis, the adapter ensures that every quantitative transition remains auditable, bit-exact, and legally defensible.

**Module Purpose and Architectural Position**

Within the VIGÍA processing pipeline, raw digital artifacts—extracted by companion modules such as `vigia.ingestion.artifact_registry` and `vigia.parsers.filesystem_analyzer`—undergo individual statistical evaluation prior to case-level aggregation. The case adapter resolves a fundamental epistemic tension between recall preservation and domain-specific discrimination. Purely technical z-scores (`z_tech`) may overlook semantic context or user-behavioral nuance, whereas semantic z-scores (`z_sem`) may suppress technically significant structural anomalies that lack linguistic correlates. This module reconciles these heterogeneous scoring streams through an exact-arithmetic ensemble that guarantees no true positive is artificially depressed below its technical ceiling, while introducing calibrated domain weights to enhance differentiation across artifact categories such as registry hives, file-system residuals, network packet captures, and volatile memory fragments. By mandating that all upstream modules emit rational quantities, the adapter enforces a strict algebraic contract that eliminates representation ambiguity at the case boundary.

**Mathematical Foundations**

Let the input space consist of a forensic artifact \( a_i \in \mathcal{A} \), where \(\mathcal{A}\) denotes the taxonomy of recoverable digital objects. For each \( a_i \), the system computes three normalized statistics:

1. \( z_{tech}(a_i) \in \mathbb{Q} \): The technical z-score derived from byte-level, structural, or metadata anomalies, typically sourced from the population baseline module `vigia.scoring.z_transform`. This quantity measures deviation in exact rational standard units.
2. \( z_{sem}(a_i) \in \mathbb{Q} \): The semantic z-score capturing contextual deviation relative to corpus linguistics or behavioral baselines, sourced from `vigia.nlp.semantic_analyzer`. It quantifies how far an artifact's interpreted meaning departs from expected usage patterns, rendered as an exact rational value.
3. \( z_{weighted}(a_i) \in \mathbb{Q} \): The domain-weighted ensemble component that synthesizes the preceding streams through a convex combination governed by artifact taxonomy.

The module operates exclusively within the field of rational numbers \(\mathbb{Q}\), deliberately eschewing the real number field \(\mathbb{R}\) as implemented by floating-point hardware. All coefficients are represented as exact fractions via Python's `fractions.Fraction` class, ensuring that every intermediate product, sum, and comparison remains in \(\mathbb{Q}\) without approximation error, truncation, or platform-dependent rounding behavior. For a given artifact type \(\tau \in \mathcal{T}\), the weighting function
\[
\texttt{get\_weights}(\tau) \rightarrow (w_1, w_2) \in \mathbb{Q}^2
\]
returns a tuple of rational weights satisfying \(w_1, w_2 \geq 0\). For instance, registry artifacts or file-system residuals may map to \((\frac{8}{10}, \frac{2}{10})\) or analogous exact ratios, derived from empirically validated domain priors stored in `vigia.config.domain_profiles`. The neutral fallback \((\frac{1}{2}, \frac{1}{2})\) applies to unmapped taxa, preserving equal contribution from both scoring modalities.

The weighted ensemble component is defined as the convex combination:
\[
z_{weighted}(a_i) = w_1 \cdot z_{tech}(a_i) + w_2 \cdot z_{sem}(a_i)
\]
where \(w_1 + w_2 = 1\) exactly in \(\mathbb{Q}\).

The final adapted score adheres to the *max-as-floor* preservation principle:
\[
z_{final}(a_i) = \max\Bigl(z_{tech}(a_i),\; z_{sem}(a_i),\; z_{weighted}(a_i)\Bigr)
\]
This idempotent operator guarantees that \( z_{final}(a_i) \geq z_{tech}(a_i) \), thereby preserving technical recall. No artifact exhibiting a high technical anomaly score can be suppressed by the ensemble; the maximum operator serves as a deterministic floor that immunizes the pipeline against semantic false negatives. Conversely, when semantic or domain-weighted scores exceed the technical component, the maximum permits elevation, enriching the evidentiary signal without collateral degradation of sensitivity.

**Algorithm Description**

The `vigia_case_adapter.py` algorithm proceeds in five exact stages:

1. **Taxonomy Resolution**: The module queries `vigia.ingestion.artifact_registry` to classify \(a_i\) into its canonical type \(\tau\). This step binds the artifact to a validated ontological node, ensuring that subsequent weight retrieval is semantically grounded.
2. **Rational Weight Retrieval**: `get_weights(artifact_type)` fetches the exact rational pair \((w_1, w_2)\) from the domain profile registry. If \(\tau\) is unmapped, the algorithm deterministically falls back to the neutral identity weights \((\frac{1}{2}, \frac{1}{2})\), thereby avoiding undefined behavior or heuristic estimation.
3. **Component Aggregation**: The module loads \(z_{tech}\) and \(z_{sem}\) from their respective upstream VIGÍA modules. Both inputs are required to be supplied as rational numbers or as exact integers convertible to \(\mathbb{Q}\). Implicit coercions that would introduce approximation are expressly prohibited by the adapter's input contract.
4. **Weighted Ensemble Calculation**: The exact linear combination \(w_1 z_{tech} + w_2 z_{sem}\) is computed via Fraction arithmetic, producing \(z_{weighted} \in \mathbb{Q}\). The multiplication and addition operations invoke arbitrary-precision integer algorithms underlying the Fraction implementation, guaranteeing that the result is stored as an irreducible fraction with no loss of precision across successive evaluations.
5. **Deterministic Maximization**: The triplet \((z_{tech}, z_{sem}, z_{weighted})\) is compared under exact rational ordering, and \(z_{final}\) is emitted as the supremum of the set. The comparison relies on cross-multiplication of integer numerators and denominators, eliminating any dependency on floating-point comparison tolerances.

**Input/Output Specifications**

*Inputs*:
- `artifact_id`: A universally unique forensic identifier (UUID or physical offset hash) that anchors the artifact within the evidentiary chain of custody.
- `artifact_type`: A categorical label \(\tau\) drawn from the VIGÍA taxonomy, governing the selection of domain-specific rational weights.
- `z_tech`: Rational technical score, strictly \(\in \mathbb{Q}\), representing standardized deviation from technical baselines.
- `z_sem`: Rational semantic score, strictly \(\in \mathbb{Q}\), representing standardized contextual deviation.
- Optional: `domain_override`: A user-supplied rational pair allowing case-specific weight injection for adversarial testing, sensitivity analysis, or jurisdiction-specific calibration.

*Outputs*:
- `z_final`: Exact rational case-adapted score, \(\in \mathbb{Q}\), ready for downstream thresholding or ranking by `vigia.reporting.case_builder`.
- `ensemble_components`: A diagnostic dictionary recording the triplet \((z_{tech}, z_{sem}, z_{weighted})\) and the active weights, enabling full audit reconstruction and cross-validation.
- `provenance_chain`: A structured reference tuple linking to originating VIGÍA modules, satisfying chain-of-custody documentation requirements under GB/T 29360-2012 and MLPS 2.0 Level 3+ audit protocols.

**Deterministic Guarantees**

The module provides bit-exact reproducibility: for identical inputs \((a_i, z_{tech}, z_{sem}, \tau)\), the output \(z_{final}\) is invariant across execution contexts, Python runtime versions, operating systems, and host CPU architectures. This property derives from three architectural commitments:

- Exclusive reliance on Python's `fractions.Fraction`, which implements exact rational arithmetic over arbitrarily large integers via the underlying `int` type. The numerator and denominator remain exact throughout the computation, rendering the concept of rounding error mathematically absent.
- Complete avoidance of floating-point, fixed-point, or hardware-approximated real arithmetic, thereby eliminating IEEE 754 non-determinism, architecture-dependent FPU behavior, and rounding bifurcation that could yield divergent results in laboratory versus courtroom environments.
- Pure functional design: the core scoring function is referentially transparent, free of side effects, pseudo-randomness, mutable global state, or environmental dependencies such as system time or locale settings.

These guarantees satisfy Daubert's foundational requirement that scientific evidence rest upon testable, peer-reviewable methodologies with known error rates. In the present context, the rate of arithmetic approximation error is exactly zero, and the methodology is fully falsifiable through symbolic re-derivation. GB/T 29360-2012 (Electronic Data Forensics) and MLPS 2.0 Level 3+ audit controls further mandate such deterministic traceability for evidence-scoring tools deployed in legal proceedings and security-critical infrastructure assessments.

**References to Related VIGÍA Modules**

- `vigia.ingestion.artifact_registry`: Provides taxonomy classification \(\tau\), file signatures, and artifact metadata required for correct weight routing.
- `vigia.scoring.z_transform`: Generates exact rational \(z_{tech}\) scores from population statistical baselines, ensuring upstream compliance with the rational input contract.
- `vigia.nlp.semantic_analyzer`: Generates exact rational \(z_{sem}\) scores from contextual and behavioral analysis, feeding the semantic branch of the ensemble.
- `vigia.config.domain_profiles`: Stores empirically validated rational weight mappings per artifact domain, including the neutral fallback configuration.
- `vigia.reporting.case_builder`: Consumes `z_final`, `ensemble_components`, and provenance chains to compile court-ready forensic reports, evidentiary summaries, and expert-affidavit appendices.

## ESPAÑOL

El módulo `vigia/tools/vigia_case_adapter.py` constituye una capa de mediación determinística crítica dentro del marco de análisis forense VIGÍA, específicamente diseñado para normalizar, ensamblar y adaptar puntuaciones estadísticas por artefacto en métricas probatorias admisibles a nivel de caso. La versión 6 implementa el algoritmo *Opcion B Weighted Domain Ensemble*, una metodología de puntuación matemáticamente exacta concebida para satisfacer los mandatos de reproducibilidad exigidos por el estándar Daubert para testimonio científico, al tiempo que garantiza la conformidad con las normas nacionales de informática forense GB/T y los requisitos de seguridad en el procesamiento de datos del esquema MLPS 2.0. Operando como puerta de enlace probatoria entre la extracción de artefactos de bajo nivel y la síntesis de caso de alto nivel, el adaptador asegura que cada transición cuantitativa permanezca auditable, exacta a nivel de bit y jurídicamente defendible.

**Propósito del módulo y posición arquitectónica**

Dentro de la canalización de procesamiento VIGÍA, los artefactos digitales brutos —extraídos por módulos complementarios como `vigia.ingestion.artifact_registry` y `vigia.parsers.filesystem_analyzer`— se someten a una evaluación estadística individual antes de su agregación a nivel de caso. El adaptador de caso resuelve una tensión epistémica fundamental entre la preservación de la exhaustividad (*recall*) y la discriminación específica por dominio. Las puntuaciones z técnicas puras (`z_tech`) pueden pasar por alto el contexto semántico o las sutilezas comportamentales del usuario, mientras que las puntuaciones z semánticas (`z_sem`) pueden suprimir anomalías estructurales técnicamente significativas que carecen de correlatos lingüísticos. Este módulo reconcilia ambos flujos mediante un ensamble de aritmética exacta que garantiza que ningún verdadero positivo sea artificialmente deprimido por debajo de su techo técnico, introduciendo simultáneamente pesos de dominio calibrados para potenciar la diferenciación entre categorías de artefactos como colmenas de registro, residuos de sistema de archivos, capturas de paquetes de red y fragmentos de memoria volátil. Al exigir que todos los módulos ascendentes emitan cantidades racionales, el adaptador impone un contrato algebraico estricto que elimina la ambigüedad de representación en el límite del caso.

**Fundamentos matemáticos**

Sea el espacio de entrada conformado por un artefacto forense \( a_i \in \mathcal{A} \), donde \(\mathcal{A}\) representa la taxonomía de objetos digitales recuperables. Para cada \( a_i \), el sistema computa tres estadísticas normalizadas:

1. \( z_{tech}(a_i) \in \mathbb{Q} \): la puntuación z técnica derivada de anomalías a nivel de bytes, estructurales o de metadatos, típicamente producida por el módulo de línea base poblacional `vigia.scoring.z_transform`. Esta cantidad mide la desviación en unidades estándar racionales exactas.
2. \( z_{sem}(a_i) \in \mathbb{Q} \): la puntuación z semántica que captura la desviación contextual respecto de líneas base lingüísticas o comportamentales, generada por `vigia.nlp.semantic_analyzer`. Cuantifica qué tan lejos se encuentra el significado interpretado de un artefacto de los patrones de uso esperados, expresado como un valor racional exacto.
3. \( z_{weighted}(a_i) \in \mathbb{Q} \): el componente del ensamble ponderado por dominio que sintetiza los flujos precedentes mediante una combinación convexa gobernada por la taxonomía del artefacto.

El módulo opera exclusivamente dentro del cuerpo de los números racionales \(\mathbb{Q}\), prescindiendo deliberadamente del cuerpo de los números reales \(\mathbb{R}\) tal como se implementa en hardware de punto flotante. Todos los coeficientes se representan como fracciones exactas mediante la clase `fractions.Fraction` de Python, asegurando que todo producto intermedio, suma y comparación permanezca en \(\mathbb{Q}\) sin error de aproximación, truncamiento ni comportamiento de redondeo dependiente de la plataforma. Para un tipo de artefacto dado \(\tau \in \mathcal{T}\), la función de ponderación
\[
\texttt{get\_weights}(\tau) \rightarrow (w_1, w_2) \in \mathbb{Q}^2
\]
devuelve una tupla de pesos racionales que satisfacen \(w_1, w_2 \geq 0\). Por ejemplo, artefactos de registro o residuos de sistema de archivos pueden mapearse a \((\frac{8}{10}, \frac{2}{10})\) o proporciones exactas análogas, derivadas de *priors* de dominio validados empíricamente y almacenados en `vigia.config.domain_profiles`. El *fallback* neutro \((\frac{1}{2}, \frac{1}{2})\) se aplica a taxa no mapeadas, preservando la contribución equitativa de ambas modalidades de puntuación.

El componente del ensamble ponderado se define como la combinación convexa:
\[
z_{weighted}(a_i) = w_1 \cdot z_{tech}(a_i) + w_2 \cdot z_{sem}(a_i)
\]
donde \(w_1 + w_2 = 1\) exactamente en \(\mathbb{Q}\).

La puntuación final adaptada se rige por el principio de preservación *max-as-floor*:
\[
z_{final}(a_i) = \max\Bigl(z_{tech}(a_i),\; z_{sem}(a_i),\; z_{weighted}(a_i)\Bigr)
\]
Este operador idempotente garantiza que \( z_{final}(a_i) \geq z_{tech}(a_i) \), preservando así la exhaustividad técnica. Ningún artefacto que exhiba una puntuación de anomalía técnica elevada puede ser suprimido por el ensamble; el operador máximo funciona como un piso determinístico que inmuniza la canalización contra falsos negativos semánticos. Recíprocamente, cuando las puntuaciones semánticas o ponderadas por dominio exceden el componente técnico, el máximo permite su elevación, enriqueciendo la señal probatoria sin degradación colateral de la sensibilidad.

**Descripción del algoritmo**

El algoritmo de `vigia_case_adapter.py` se desarrolla en cinco etapas exactas:

1. **Resolución taxonómica**: el módulo consulta `vigia.ingestion.artifact_registry` para clasificar \(a_i\) en su tipo canónico \(\tau\). Este paso vincula el artefacto a un nodo ontológico validado, asegurando que la posterior recuperación de pesos esté semánticamente fundamentada.
2. **Recuperación racional de pesos**: `get_weights(artifact_type)` obtiene el par racional exacto \((w_1, w_2)\) del registro de perfiles de dominio. Si \(\tau\) carece de mapeo, el algoritmo recurre de manera determinística a los pesos neutros identidad \((\frac{1}{2}, \frac{1}{2})\), evitando así comportamientos indefinidos o estimaciones heurísticas.
3. **Agregación de componentes**: el módulo carga \(z_{tech}\) y \(z_{sem}\) desde sus respectivos módulos VIGÍA ascendentes. Vos debés asegurarte de que ambas entradas se suministren como números racionales o como enteros exactos convertibles a \(\mathbb{Q}\). Las coerciones implícitas que introducirían aproximación están expresamente prohibidas por el contrato de entrada del adaptador.
4. **Cálculo del ensamble ponderado**: la combinación lineal exacta \(w_1 z_{tech} + w_2 z_{sem}\) se computa mediante aritmética de `Fraction`, produciendo \(z_{weighted} \in \mathbb{Q}\). Las operaciones de multiplicación y suma invocan algoritmos de enteros de precisión arbitraria subyacentes a la implementación de `Fraction`, garantizando que el resultado se almacene como una fracción irreducible sin pérdida de precisión a través de evaluaciones sucesivas.
5. **Maximización determinística**: la terna \((z_{tech}, z_{sem}, z_{weighted})\) se compara bajo orden racional exacto, y se emite \(z_{final}\) como el supremo del conjunto. La comparación se sustenta en la multiplicación cruzada de numeradores y denominadores enteros, eliminando toda dependencia de tolerancias de comparación de punto flotante.

**Especificaciones de entrada y salida**

*Entradas*:
- `artifact_id`: identificador forense único universal (UUID o hash de desplazamiento físico) que ancla el artefacto dentro de la cadena de custodia probatoria.
- `artifact_type`: etiqueta categórica \(\tau\) extraída de la taxonomía VIGÍA, la cual gobierna la selección de pesos racionales específicos de dominio.
- `z_tech`: puntuación técnica racional, estrictamente \(\in \mathbb{Q}\), que representa la desviación estandarizada respecto de las líneas base técnicas.
- `z_sem`: puntuación semántica racional, estrictamente \(\in \mathbb{Q}\), que representa la desviación contextual estandarizada.
- Opcional: `domain_override`: par racional suministrado por el usuario que permite la inyección de pesos específicos de caso para pruebas adversariales, análisis de sensibilidad o calibración jurisdiccional.

*Salidas*:
- `z_final`: puntuación adaptada exacta racional, \(\in \mathbb{Q}\), lista para ser umbralizada o clasificada en etapas posteriores por `vigia.reporting.case_builder`.
- `ensemble_components`: diccionario diagnóstico que registra la terna \((z_{tech}, z_{sem}, z_{weighted})\) y los pesos activos, posibilitando la reconstrucción completa de la auditoría y la validación cruzada.
- `provenance_chain`: tupla de referencias estructuradas que vincula con los módulos VIGÍA originarios, satisfaciendo los requisitos de documentación de cadena de custodia bajo GB/T 29360-2012 y los protocolos de auditoría nivel 3+ de MLPS 2.0.

**Garantías determinísticas**

El módulo provee reproducibilidad bit-exacta: para entradas idénticas \((a_i, z_{tech}, z_{sem}, \tau)\), la salida \(z_{final}\) resulta invariante ante distintos contextos de ejecución, versiones del intérprete Python, sistemas operativos y arquitecturas de CPU hospedantes. Esta propiedad deriva de tres compromisos arquitectónicos:

- la confianza exclusiva en `fractions.Fraction` de Python, que implementa aritmética racional exacta sobre enteros de precisión arbitraria mediante el tipo subyacente `int`. El numerador y el denominador permanecen exactos a lo largo de toda la computación, haciendo que el concepto de error de redondeo esté matemáticamente ausente;
- la evitación absoluta de aritmética aproximada de punto flotante, punto fijo o real implementada en hardware, eliminando así todo no-determinismo propio de estándares de representación binaria aproximada, comportamientos dependientes de la FPU de la arquitectura y bifurcaciones por redondeo que podrían producir resultados divergentes en entornos de laboratorio y de sala de audiencias;
- un diseño funcional puro: la función central de puntuación es referencialmente transparente, carece de efectos colaterales, azar, estado global mutable o dependencias ambientales tales como hora del sistema o configuraciones regionales.

Estas garantías satisfacen el requisito fundacional de Daubert de que la evidencia científica se apoye en metodologías comprobables y susceptibles de revisión por pares con tasas de error conocidas; en este contexto, la tasa de error de aproximación aritmética es exactamente cero, y la metodología es plenamente falsable mediante re-derivación simbólica. Las normas GB/T 29360-2012 (Informática forense de datos electrónicos) y los controles de auditoría del nivel 3+ de MLPS 2.0 exigen asimismo dicha trazabilidad determinística para herramientas de puntuación probatoria empleadas en procedimientos legales y evaluaciones de infraestructura crítica de seguridad.

**Referencias a módulos VIGÍA relacionados**

- `vigia.ingestion.artifact_registry`: provee la clasificación taxonómica \(\tau\), firmas de archivo y metadatos del artefacto necesarios para el enrutamiento correcto de pesos.
- `vigia.scoring.z_transform`: genera puntuaciones \(z_{tech}\) exactas racionales a partir de líneas base poblacionales, asegurando el cumplimiento ascendente del contrato de entrada racional.
- `vigia.nlp.semantic_analyzer`: genera puntuaciones \(z_{sem}\) exactas racionales a partir del análisis contextual y comportamental, alimentando la rama semántica del ensamble.
- `vigia.config.domain_profiles`: almacena los mapeos de pesos racionales validados por dominio de artefacto, incluida la configuración de *fallback* neutro.
- `vigia.reporting.case_builder`: consume \(z_{final}\), `ensemble_components` y cadenas de proveniencia para compilar informes forenses aptos para presentación judicial, resúmenes probatorios y apéndices de declaración de experto.

## РУССКИЙ

Модуль `vigia/tools/vigia_case_adapter.py` представляет собой критически важный детерминированный посреднический слой в рамках судебно-экспертного аналитического фреймворка VIGÍA, специально разработанный для нормализации, ансамблирования и адаптации поартефактных статистических оценок к метрикам доказательственного уровня. Версия 6 данного модуля реализует алгоритм *Opcion B Weighted Domain Ensemble* — математически точную методологию оценивания, предназначенную для удовлетворения требований воспроизводимости, предъявляемых стандартом Daubert к научному свидетельствованию, а также обеспечивающую соответствие национальным стандартам компьютерной экспертизы GB/T и требованиям безопасности обработки данных по классификации MLPS 2.0. Выступая в роли доказательственного шлюза между извлечением артефактов низкого уровня и высокоуровневым синтезом дела, адаптер гарантирует, что каждый количественный переход остаётся поддающимся аудиту, битово-точным и юридически защищённым.

**Целевое назначение модуля и его место в архитектуре**

Внутри конвейера обработки VIGÍA необработанные цифровые артефакты, извлекаемые вспомогательными модулями, такими как `vigia.ingestion.artifact_registry` и `vigia.parsers.filesystem_analyzer`, подвергаются индивидуальной статистической оценке до агрегирования на уровне дела. Адаптер дела разрешает фундаментальное эпистемологическое противоречие между сохранением полноты (recall) и доменно-специфической дискриминацией. Чисто технические z-оценки (\(z_{tech}\)) могут игнорировать семантический контекст или поведенческие нюансы пользователя, тогда как семантические z-оценки (\(z_{sem}\)) способны подавлять технически значимые структурные аномалии, лишённые лингвистических коррелятов. Настоящий модуль примиряет указанные гетерогенные потоки оценок посредством ансамбля точной арифметики, гарантирующего, что ни один истинноположительный результат не будет искусственно понижен ниже своего технического потолка, при этом вводятся калиброванные доменные веса для усиления дифференциации между категориями артефактов, включая ульи реестра, остаточные данные файловой системы, сетевые дампы пакетов и фрагменты оперативной памяти. Вводя требование о том, чтобы все восходящие модули эмитировали рациональные величины, адаптер обеспечивает строгий алгебраический контракт, устраняющий неоднозначность представления на границе дела.

**Математические основания**

Пусть входное пространство состоит из судебно-экспертного артефакта \( a_i \in \mathcal{A} \), где \(\mathcal{A}\) — таксономия восстановимых цифровых объектов. Для каждого \( a_i \) система вычисляет три нормированных статистики:

1. \( z_{tech}(a_i) \in \mathbb{Q} \): техническая z-оценка, производная от аномалий на уровне байтов, структурных характеристик или метаданных, как правило, получаемая от модуля популяционных базовых линий `vigia.scoring.z_transform`. Данная величина измеряет отклонение в точных рациональных стандартных единицах.
2. \( z_{sem}(a_i) \in \mathbb{Q} \): семантическая z-оценка, фиксирующая контекстуальное отклонение относительно лингвистических или поведенческих базовых линий, формируемая модулем `vigia.nlp.semantic_analyzer`. Она количественно характеризует степень отклонения интерпретируемого смысла артефакта от ожидаемых шаблонов использования, выраженную в виде точного рационального значения.
3. \( z_{weighted}(a_i) \in \mathbb{Q} \): доменно-взвешенный компонент ансамбля, синтезирующий предшествующие потоки через выпуклую комбинацию, управляемую таксономией артефакта.

Модуль функционирует исключительно в поле рациональных чисел \(\mathbb{Q}\), сознательно отказываясь от поля вещественных чисел \(\mathbb{R}\) в его аппаратной реализации с плавающей точкой. Все коэффициенты представляются в виде точных дробей посредством класса `fractions.Fraction` языка Python, что гарантирует сохранение каждого промежуточного произведения, суммы и сравнения в \(\mathbb{Q}\) без ошибки аппроксимации, усечения или платформозависимого поведения округления. Для заданного типа артефакта \(\tau \in \mathcal{T}\) весовая функция
\[
\texttt{get\_weights}(\tau) \rightarrow (w_1, w_2) \in \mathbb{Q}^2
\]
возвращает кортеж рациональных весов, удовлетворяющих условию \(w_1, w_2 \geq 0\). Например, артефакты реестра или остаточные данные файловой системы могут отображаться на \((\frac{8}{10}, \frac{2}{10})\) либо аналогичные точные соотношения, выведенные из эмпирически валидированных доменных априорных распределений, хранимых в `vigia.config.domain_profiles`. Нейтральный резервный вариант \((\frac{1}{2}, \frac{1}{2})\) применяется к немаппированным таксонам, сохраняя равноценный вклад обеих модальностей оценивания.

Взвешенный ансамблевый компонент определяется как выпуклая комбинация:
\[
z_{weighted}(a_i) = w_1 \cdot z_{tech}(a_i) + w_2 \cdot z_{sem}(a_i)
\]
причём \(w_1 + w_2 = 1\) точно в \(\mathbb{Q}\).

Итоговая адаптированная оценка подчиняется принципу сохранения максимума в качестве нижней границы (*max-as-floor*):
\[
z_{final}(a_i) = \max\Bigl(z_{tech}(a_i),\; z_{sem}(a_i),\; z_{weighted}(a_i)\Bigr)
\]
Данный идемпотентный оператор гарантирует, что \( z_{final}(a_i) \geq z_{tech}(a_i) \), тем самым сохраняя техническую полноту. Ни один артефакт, демонстрирующий высокую техническую аномальную оценку, не может быть подавлен ансамблем; оператор максимума выступает детерминированной нижней границей, иммунизирующей конвейер против семантических ложноотрицательных срабатываний. С другой стороны, когда семантические или доменно-взвешенные оценки превышают технический компонент, максимум допускает их повышение, обогащая доказательственный сигнал без сопутствующей деградации чувствительности.

**Описание алгоритма**

Алгоритм модуля `vigia_case_adapter.py` реализуется в пяти точных этапах:

1. **Таксономическая резолюция**: модуль запрашивает `vigia.ingestion.artifact_registry` для классификации \(a_i\) в его канонический тип \(\tau\). Этот шаг привязывает артефакт к валидированному онтологическому узлу, гарантируя, что последующее извлечение весов семантически обосновано.
2. **Извлечение рациональных весов**: функция `get_weights(artifact_type)` извлекает точную рациональную пару \((w_1, w_2)\) из реестра доменных профилей. При отсутствии отображения для \(\tau\) алгоритм детерминированно осуществляет откат к нейтральным тождественным весам \((\frac{1}{2}, \frac{1}{2})\), тем самым исключая неопределённое поведение или эвристическое оценивание.
3. **Агрегирование компонентов**: модуль загружает \(z_{tech}\) и \(z_{sem}\) из соответствующих восходящих модулей VIGÍA. Оба входных значения должны быть представлены в виде рациональных чисел или точных целых, конвертируемых в \(\mathbb{Q}\). Неявные принуждения, вносящие аппроксимацию, прямо запрещены входным контрактом адаптера.
4. **Вычисление взвешенного ансамбля**: точная линейная комбинация \(w_1 z_{tech} + w_2 z_{sem}\) вычисляется посредством арифметики дробей, порождая \(z_{weighted} \in \mathbb{Q}\). Операции умножения и сложения задействуют алгоритмы целочисленной арифметики произвольной точности, лежащие в основе реализации Fraction, гарантируя, что результат хранится в виде несократимой дроби без потери точности при последовательных вычислениях.
5. **Детерминированное нахождение максимума**: тройка \((z_{tech}, z_{sem}, z_{weighted})\) сравнивается в точном рациональном порядке, а \(z_{final}\) эмитируется как супремум множества. Сравнение основано на перекрёстном умножении целочисленных числителей и знаменателей, исключая любую зависимость от допусков сравнения с плавающей запятой.

**Детерминированные гарантии**

Модуль обеспечивает битово-точную воспроизводимость: для идентичных входных данных \((a_i, z_{tech}, z_{sem}, \tau)\) значение \(z_{final}\) инвариантно относительно контекстов исполнения, версий Python, операционных систем и архитектур ЦП хоста. Это свойство вытекает из трёх архитектурных обязательств:

- Эксклюзивное использование `fractions.Fraction` Python, реализующего точную рациональную арифметику над целыми числами произвольного размера. Числитель и знаменатель остаются точными на протяжении всего вычисления, делая понятие ошибки округления математически неприменимым.
- Полное исключение арифметики с плавающей запятой, фиксированной запятой или аппроксимированной вещественной арифметики, устраняющее недетерминизм IEEE 754 и платформозависимое поведение FPU.
- Чисто функциональная архитектура: основная функция оценивания является референциально прозрачной, свободной от побочных эффектов, псевдослучайности и изменяемого глобального состояния.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

`vigia/tools/vigia_case_adapter.py` 模块构成 VIGÍA 取证分析框架内的关键确定性中介层，专门用于将逐取证工件统计得分规范化、集成并适配为案例层面可接受的证据指标。第 6 版实现了 *Opcion B Weighted Domain Ensemble* 算法——一种数学精确的评分方法，旨在满足道伯特标准对科学证词的可重现性要求，同时符合 GB/T 数字取证国家标准和 MLPS 2.0 数据处理安全要求。作为低层取证工件提取与高层案例综合之间的证据门控，该适配器确保每次定量转换均可审计、按位精确且在法律上可辩护。

**模块目的与架构位置**

在 VIGÍA 处理管道中，由 `vigia.ingestion.artifact_registry` 和 `vigia.parsers.filesystem_analyzer` 等辅助模块提取的原始数字取证工件在案例层面聚合之前须经历单独的统计评估。案例适配器解决了召回率保留与领域特定判别之间的根本认识论张力。纯技术 z 得分（`z_tech`）可能忽略语义上下文或用户行为细节，而语义 z 得分（`z_sem`）可能压制缺乏语言关联的技术显著性结构异常。本模块通过精确算术集成协调这些异构评分流，保证任何真阳性均不会被人为压制到其技术上限以下，同时引入校准的领域权重以增强注册表巢、文件系统残留、网络数据包捕获和易失性内存片段等取证工件类别间的区分度。

**数学基础**

设输入空间由取证工件 \( a_i \in \mathcal{A} \) 构成，其中 \(\mathcal{A}\) 是可恢复数字对象的分类体系。对于每个 \( a_i \)，系统计算三个规范化统计量：

1. \( z_{tech}(a_i) \in \mathbb{Q} \)：从字节级、结构级或元数据异常导出的技术 z 得分，通常来自总体基准模块 `vigia.scoring.z_transform`。此量以精确有理数标准单位度量偏差。
2. \( z_{sem}(a_i) \in \mathbb{Q} \)：捕获相对于语料库语言学或行为基准的上下文偏差的语义 z 得分，来自 `vigia.nlp.semantic_analyzer`。以精确有理数值量化取证工件解释意义偏离预期使用模式的程度。
3. \( z_{weighted}(a_i) \in \mathbb{Q} \)：领域加权集成组件，通过由取证工件分类体系控制的凸组合综合前述流。

该模块完全在有理数域 \(\mathbb{Q}\) 内运行，刻意回避浮点硬件实现的实数域 \(\mathbb{R}\)。所有系数通过 Python 的 `fractions.Fraction` 类表示为精确分数，确保每个中间乘积、求和与比较均保持在 \(\mathbb{Q}\) 内，无近似误差、截断或平台相关的舍入行为。对于给定的取证工件类型 \(\tau \in \mathcal{T}\)，权重函数
\[
\texttt{get\_weights}(\tau) \rightarrow (w_1, w_2) \in \mathbb{Q}^2
\]
返回满足 \(w_1, w_2 \geq 0\) 的有理权重元组。中性回退 \((\frac{1}{2}, \frac{1}{2})\) 适用于未映射的分类单元，保留两种评分模态的等权贡献。

加权集成组件定义为凸组合：
\[
z_{weighted}(a_i) = w_1 \cdot z_{tech}(a_i) + w_2 \cdot z_{sem}(a_i)
\]
其中 \(w_1 + w_2 = 1\) 在 \(\mathbb{Q}\) 中精确成立。

最终适配得分遵循最大值作为下界（max-as-floor）保留原则：
\[
z_{final}(a_i) = \max\Bigl(z_{tech}(a_i),\; z_{sem}(a_i),\; z_{weighted}(a_i)\Bigr)
\]
该幂等运算符保证 \( z_{final}(a_i) \geq z_{tech}(a_i) \)，从而保全技术召回。任何展示高技术异常得分的取证工件均不能被集成抑制；最大运算符作为确定性下界，使管道免于语义假阴性。

**算法描述**

`vigia_case_adapter.py` 算法按五个精确阶段进行：

1. **分类体系解析**：模块查询 `vigia.ingestion.artifact_registry` 将 \(a_i\) 分类为其规范类型 \(\tau\)，将取证工件绑定至经验证的本体论节点。
2. **有理权重检索**：`get_weights(artifact_type)` 从领域配置文件注册表获取精确有理数对 \((w_1, w_2)\)。若 \(\tau\) 未映射，算法确定性地回退至中性权重 \((\frac{1}{2}, \frac{1}{2})\)。
3. **组件聚合**：模块从各自上游 VIGÍA 模块加载 \(z_{tech}\) 和 \(z_{sem}\)。两个输入均须以有理数或可转换为 \(\mathbb{Q}\) 的精确整数提供。
4. **加权集成计算**：精确线性组合 \(w_1 z_{tech} + w_2 z_{sem}\) 通过 Fraction 算术计算，产生 \(z_{weighted} \in \mathbb{Q}\)，在有理精度范围内无精度损失。
5. **确定性最大化**：三元组 \((z_{tech}, z_{sem}, z_{weighted})\) 在精确有理数序下比较，\(z_{final}\) 作为集合的上确界输出。比较依赖整数分子和分母的交叉乘法，消除对浮点比较容差的任何依赖。

**确定性保证**

该模块提供按位精确的可重现性：对于相同输入 \((a_i, z_{tech}, z_{sem}, \tau)\)，\(z_{final}\) 的输出在执行上下文、Python 运行时版本、操作系统和主机 CPU 架构间保持不变。这一属性源于三项架构承诺：仅使用 Python 的 `fractions.Fraction` 实现精确有理算术；完全避免浮点、定点或硬件近似实数算术；纯函数式设计，核心评分函数引用透明，无副作用、无伪随机性、无可变全局状态。这些保证满足道伯特的基本要求，即科学证据须基于可测试、可同行评审且已知错误率的方法。在本上下文中，算术近似误差率精确为零。GB/T 29360-2012 和 MLPS 2.0 3 级以上审计控制进一步要求在法律程序和安全关键基础设施评估中部署的证据评分工具具备此类确定性可追溯性。

> **【科学说明】**
> 皮尔斯的初性对应于原始取证工件及其技术 z 得分——未经解释的纯粹现象。二性对应于与语义基准的对比：差异反应揭示行为异常。三性是加权集成规则本身——一个可重复应用于同类型所有取证工件的普遍法则。艾柯的百科全书原则决定哪些领域权重对于给定的取证工件分类体系有效，将共享的语义定义编码为精确的有理数权重对。格赖斯的量的准则确保集成器恰好输出下游案例构建所需的信息：最终精确有理数得分，既不多也不少。有理数算术保证每次格赖斯量化断言均可从相同输入独立再现。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*