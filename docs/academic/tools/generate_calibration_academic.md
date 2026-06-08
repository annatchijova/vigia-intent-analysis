## ENGLISH

**Module Identifier:** `vigia/tools/generate_calibration.py`

**1. Module Purpose and System Context**

The module `generate_calibration.py` constitutes a deterministic data-transformation stage within the VIGÍA forensic analysis pipeline. Its primary function is to convert the annotated evidentiary corpus `vigia_60_cases_dataset.json`—comprising sixty textual artifacts with established ground-truth labels—into a structured calibration dataset suitable for probabilistic model training. In the broader VIGÍA architecture, this module occupies the boundary between raw evidence ingestion and statistical model fitting. It bridges the output of the semiotic detection engine and the input requirements of the calibration fitting procedure, ensuring that downstream probability estimates are derived from standardized, reproducible feature vectors rather than from raw, unprocessed text.

From a forensic methodology perspective, an uncalibrated detector yields unbounded raw scores that lack probabilistic interpretability under courtroom admissibility standards. By transforming the evidentiary corpus into z-score vectors, this module supplies the necessary intermediate representation upon which `fit_calibration.py` can subsequently learn a mapping from feature space to the probability simplex $[0,1]$. The transformation is therefore not merely a syntactic reformatting operation; it is an epistemic prerequisite for producing forensically valid posterior likelihoods.

**2. Mathematical Foundations**

Let the input corpus be defined as an ordered set $D = \{d_1, d_2, \ldots, d_{60}\}$, where each element $d_i$ is a tuple $d_i = (t_i, y_i)$. Here, $t_i \in \mathcal{T}$ represents a textual artifact drawn from the space of admissible UTF-8 strings, and $y_i \in \mathbb{L} = \{\text{AUTHENTIC}, \text{FABRICATED}\}$ denotes the ground-truth forensic label assigned through independent adjudication. The module implements a deterministic transformation function $\mathcal{G}: D \to C$, producing the calibration corpus $C = \{c_1, c_2, \ldots, c_{60}\}$.

Each output record $c_i$ is formally defined as:
$$c_i = \left(y_i, \mathbf{z}_i\right)$$
where $\mathbf{z}_i = (z_{i,1}, z_{i,2}, \ldots, z_{i,m}) \in \mathbb{R}^m$ is the z-score vector extracted from $t_i$ across $m$ semiotic dimensions. For a given dimension $k \in \mathcal{K}$ (e.g., $\text{SDA}$), the component $z_{i,k}$ is derived via the deterministic feature mapping $\mathcal{F}_k: \mathcal{T} \to \mathbb{R}$ instantiated by `SemioticDetectorV2`. The mapping satisfies:
$$\forall t \in \mathcal{T}, \quad \mathcal{F}_k(t) = f_{i,k} \mapsto z_{i,k}$$
where the arrow denotes the internal deterministic standardization operator $\phi_k: \mathbb{R} \to \mathbb{R}$ such that $z_{i,k} = \phi_k(f_{i,k})$. The operator $\phi_k$ is a pure function with fixed parameters; it contains no random variables, time-varying coefficients, or environment-dependent branching. The transformation $\mathcal{G}$ is thus a composition of validated parsing, feature extraction, and structural binding operations:
$$\mathcal{G} = \mathcal{B} \circ \boldsymbol{\Phi} \circ \mathcal{F}$$
with $\mathcal{F} = (\mathcal{F}_1, \ldots, \mathcal{F}_m)$, $\boldsymbol{\Phi} = (\phi_1, \ldots, \phi_m)$, and $\mathcal{B}$ the record-binding operator that pairs the label $y_i$ with the vector $\mathbf{z}_i$.

**3. Algorithm Description**

The algorithmic pipeline comprises the following strictly ordered stages:

*Stage 1 – Ingestion and Schema Validation.* The module reads `vigia_60_cases_dataset.json` and verifies that every record contains a non-null textual field and a ground-truth label belonging to $\mathbb{L}$. Any record violating the schema raises a deterministic fatal exception, halting execution to prevent contaminated calibration data. This validation step enforces domain closure over the input set and constitutes the precondition for all subsequent mathematical transformations.

*Stage 2 – Deterministic Feature Extraction.* For each validated artifact $t_i$, the module invokes `SemioticDetectorV2.compute(text=t_i)`. This engine applies a deterministic rule-based and statistically-grounded analysis to derive raw semiotic feature values $f_{i,k}$ for each dimension $k \in \mathcal{K}$. The process is entirely non-stochastic; no random sampling, Monte Carlo estimation, or probabilistic perturbation is employed. Consequently, for any fixed input $t_i$, the feature extraction operator $\mathcal{F}$ emits a constant vector across all executions.

*Stage 3 – Z-Score Standardization.* The raw features are converted into z-scores using the fixed internal parameters and precomputed population statistics embedded within `SemioticDetectorV2`. For each dimension $k$, the standardization operator $\phi_k$ maps $f_{i,k}$ to $z_{i,k}$ according to the detector’s deterministic rule set. This ensures that $z_{i,k}$ represents a fixed, comparable measure of deviation from the detector’s reference distribution, eliminating dimensional disparities that would otherwise confound downstream calibration fitting.

*Stage 4 – Record Structuring.* The module binds each ground-truth label $y_i$ with its corresponding z-score map to form the record $c_i$. The output schema enforces a bijective mapping between the input index $i$ and the output index, preserving evidentiary ordering and ensuring that no record duplication or omission occurs during transit.

*Stage 5 – Serialization.* The calibration corpus $C$ is serialized to a JSON-compliant byte stream. Numerical representations are handled via deterministic formatting rules, ensuring bitwise consistency across executions on identical hardware-software stacks and satisfying the stringent reproducibility requirements of forensic data processing.

*Stage 6 – Audit Hashing.* A cryptographic digest (SHA-256) of both the input corpus and the output corpus is computed to establish an integrity baseline for chain-of-custody documentation. This digest serves as an anchor for module-level audit trails and supports non-repudiable verification of the entire transformation.

**4. Input / Output Specifications**

*Input:* File `vigia_60_cases_dataset.json`; encoding UTF-8; schema as array of objects with keys `text` (string) and `label` (enum $\mathbb{L}$). Canonical cardinality $|D| = 60$.

*Output:* Calibration vector file; schema as array of objects with keys `ground_truth` (enum $\mathbb{L}$) and `z_scores` (object mapping dimension identifiers such as `SDA` to real-valued scalars). The output is functionally typed as $C \subset \mathbb{L} \times \mathbb{R}^m$.

**5. Deterministic Guarantees**

The module provides strict deterministic guarantees critical to forensic admissibility. Formally:
$$\forall t, t' \in \text{Exec}, \quad \mathcal{G}(D)_t = \mathcal{G}(D)_{t'}$$
meaning that for any two executions $t$ and $t'$ on the identical input corpus $D$, the output corpora $C$ are bitwise identical. This property is enforced by (a) the absence of pseudo-random number generators or true randomness sources, (b) the absence of temporal, environmental, or process-ID dependencies, (c) deterministic iteration order over collections, preventing memory-address nondeterminism from leaking into serialization order, and (d) the deterministic specification of `SemioticDetectorV2`. These guarantees satisfy the reliability prong of the Daubert standard for expert testimony, as they establish a known procedure with zero variance under identical conditions.

**6. Compliance and Standards References**

*Daubert Standard.* The module’s deterministic reproducibility, documented error conditions, and peer-reviewable logic directly support the admissibility criteria under Federal Rules of Evidence 702, providing a foundational basis for the scientific reliability of expert testimony derived from VIGÍA outputs.

*GB/T 22239-2019.* The module adheres to baseline requirements for data integrity during secondary processing of digital evidence, ensuring that no unrecorded alteration of evidentiary content occurs during transformation.

*MLPS 2.0.* Audit hashing and non-repudiable transformation logs align with Multi-Level Protection Scheme 2.0 requirements for forensic data handling, security auditing, and end-to-end traceability.

**7. Related VIGÍA Modules**

- `vigia/core/semiotic_detector_v2.py`: Supplies the deterministic feature extraction engine $\mathcal{F}$ responsible for mapping raw textual artifacts into the high-dimensional semiotic feature space.
- `vigia/tools/fit_calibration.py`: Consumes corpus $C$ to estimate the calibration mapping $\mathcal{M}: \mathbb{R}^m \to [0,1]$, typically via Platt scaling or isotonic regression, yielding posterior probabilities $P(\text{FABRICATED} \mid \mathbf{z})$.
- `vigia_60_cases_dataset.json`: The canonical annotated evidentiary corpus serving as the module's input domain; its annotation quality directly influences the generalization performance of the downstream calibration model.

## ESPAÑOL

**Identificador del módulo:** `vigia/tools/generate_calibration.py`

**1. Propósito y contexto del sistema**

Este módulo constituye una etapa determinística de transformación de datos dentro del pipeline de análisis forense de VIGÍA. Su función primordial consiste en convertir el corpus evidencial anotado `vigia_60_cases_dataset.json` —compuesto por sesenta artefactos textuales con etiquetas de verdad de campo establecidas— en un dataset de calibración estructurado, apto para el entrenamiento de modelos probabilísticos. En la arquitectura general de VIGÍA, este componente se sitúa en la frontera entre la ingestión de evidencia cruda y el ajuste estadístico del modelo. Genera un puente entre la salida del motor de detección semiótica y los requerimientos de entrada del procedimiento de ajuste de calibración, asegurando que las estimaciones de probabilidad posteriores se deriven de vectores de características estandarizados y reproducibles, en lugar de texto no procesado.

Desde una perspectiva metodológica forense, un detector no calibrado produce puntuaciones crudas no acotadas que carecen de interpretabilidad probabilística bajo los estándares de admisibilidad judicial. Al transformar el corpus evidencial en vectores de z-scores, este módulo suministra la representación intermedia necesaria para que `fit_calibration.py` aprenda posteriormente un mapeo desde el espacio de características al simplex de probabilidad $[0,1]$. Cuando integrás este módulo en el pipeline de VIGÍA, observás que su comportamiento no es una mera reformateo sintáctico, sino un prerrequisito epistémico para producir likelihoods posteriores forensicamente válidas.

**2. Fundamentos matemáticos**

Definamos el corpus de entrada como un conjunto ordenado $D = \{d_1, d_2, \ldots, d_{60}\}$, donde cada elemento $d_i$ es una tupla $d_i = (t_i, y_i)$. Aquí, $t_i \in \mathcal{T}$ representa un artefacto textual perteneciente al espacio de cadenas UTF-8 admisibles, e $y_i \in \mathbb{L} = \{\text{AUTHENTIC}, \text{FABRICATED}\}$ denota la etiqueta forense de verdad de campo asignada mediante adjudicación independiente. El módulo implementa una función de transformación determinística $\mathcal{G}: D \to C$, produciendo el corpus de calibración $C = \{c_1, c_2, \ldots, c_{60}\}$.

Cada registro de salida $c_i$ se define formalmente como:
$$c_i = \left(y_i, \mathbf{z}_i\right)$$
donde $\mathbf{z}_i = (z_{i,1}, z_{i,2}, \ldots, z_{i,m}) \in \mathbb{R}^m$ es el vector de z-scores extraído de $t_i$ a lo largo de $m$ dimensiones semióticas. Para una dimensión dada $k \in \mathcal{K}$ (por ejemplo, $\text{SDA}$), la componente $z_{i,k}$ se deriva mediante el mapeo determinístico de características $\mathcal{F}_k: \mathcal{T} \to \mathbb{R}$ instanciado por `SemioticDetectorV2`. El mapeo satisface:
$$\forall t \in \mathcal{T}, \quad \mathcal{F}_k(t) = f_{i,k} \mapsto z_{i,k}$$
donde la flecha denota el operador determinístico de estandarización interna $\phi_k: \mathbb{R} \to \mathbb{R}$ tal que $z_{i,k} = \phi_k(f_{i,k})$. El operador $\phi_k$ es una función pura con parámetros fijos; no contiene variables aleatorias, coeficientes variables en el tiempo ni ramificaciones dependientes del entorno. La transformación $\mathcal{G}$ es, por ende, una composición de operaciones de parsing validado, extracción de características y vinculación estructural:
$$\mathcal{G} = \mathcal{B} \circ \boldsymbol{\Phi} \circ \mathcal{F}$$
con $\mathcal{F} = (\mathcal{F}_1, \ldots, \mathcal{F}_m)$, $\boldsymbol{\Phi} = (\phi_1, \ldots, \phi_m)$, y $\mathcal{B}$ el operador de vinculación de registros que empareja la etiqueta $y_i$ con el vector $\mathbf{z}_i$.

**3. Descripción del algoritmo**

El pipeline algorítmico comprende las siguientes etapas estrictamente ordenadas:

*Etapa 1 – Ingesta y validación de esquema.* El módulo lee `vigia_60_cases_dataset.json` y verifica que cada registro contenga un campo textual no nulo y una etiqueta de verdad de campo perteneciente a $\mathbb{L}$. Si algún registro viola el esquema, se genera una excepción fatal determinística que detiene la ejecución para evitar la contaminación de los datos de calibración. Esta etapa de validación impone el cierre del dominio sobre el conjunto de entrada y constituye la precondición para todas las transformaciones matemáticas subsiguientes.

*Etapa 2 – Extracción determinística de características.* Para cada artefacto validado $t_i$, el módulo invoca `SemioticDetectorV2.compute(text=t_i)`. Este motor aplica un análisis determinístico basado en reglas y fundamentado estadísticamente para derivar los valores crudos de características semióticas $f_{i,k}$ para cada dimensión $k \in \mathcal{K}$. El proceso es enteramente no estocástico; no se emplean muestreos aleatorios, estimaciones Monte Carlo ni perturbaciones probabilísticas. En consecuencia, para una entrada fija $t_i$, el operador de extracción $\mathcal{F}$ emite un vector constante en todas las ejecuciones.

*Etapa 3 – Estandarización de z-scores.* Las características crudas se convierten en z-scores mediante los parámetros internos fijos y los estadísticos poblacionales precomputados embebidos en `SemioticDetectorV2`. Para cada dimensión $k$, el operador de estandarización $\phi_k$ mapea $f_{i,k}$ a $z_{i,k}$ de acuerdo con el conjunto de reglas determinísticas del detector. Esto asegura que $z_{i,k}$ represente una medida fija y comparable de desviación respecto a la distribución de referencia del detector, eliminando disparidades dimensionales que de otro modo confundirían el ajuste de calibración posterior.

*Etapa 4 – Estructuración de registros.* El módulo vincula cada etiqueta de verdad de campo $y_i$ con su mapa de z-scores correspondiente para formar el registro $c_i$. El esquema de salida impone un mapeo biyectivo entre el índice de entrada $i$ y el índice de salida, preservando el orden evidencial y asegurando que no se produzcan duplicaciones ni omisiones durante el tránsito.

*Etapa 5 – Serialización.* El corpus de calibración $C$ se serializa a un flujo de bytes compatible con JSON. Las representaciones numéricas se gestionan mediante reglas de formato deterministas, garantizando consistencia bit a bit entre ejecuciones sobre pilas idénticas de hardware y software, satisfaciendo los estrictos requisitos de reproducibilidad propios del procesamiento forense de datos.

*Etapa 6 – Hasheo de auditoría.* Se computa un resumen criptográfico (SHA-256) tanto del corpus de entrada como del corpus de salida para establecer una línea de base de integridad para la documentación de cadena de custodia. Este resumen sirve como ancla para las pistas de auditoría a nivel de módulo y soporta la verificación no repudiable de toda la transformación.

**4. Especificaciones de entrada y salida**

*Entrada:* Archivo `vigia_60_cases_dataset.json`; codificación UTF-8; esquema como arreglo de objetos con claves `text` (cadena) y `label` (enum $\mathbb{L}$). Cardinalidad canónica $|D| = 60$.

*Salida:* Archivo de vectores de calibración; esquema como arreglo de objetos con claves `ground_truth` (enum $\mathbb{L}$) y `z_scores` (objeto que mapea identificadores de dimensión tales como `SDA` a escalares de valor real). La salida está tipada funcionalmente como $C \subset \mathbb{L} \times \mathbb{R}^m$.

**5. Garantías determinísticas**

El módulo provee garantías determinísticas estrictas, críticas para la admisibilidad forense. Formalmente:
$$\forall t, t' \in \text{Exec}, \quad \mathcal{G}(D)_t = \mathcal{G}(D)_{t'}$$
lo cual significa que para cualesquiera dos ejecuciones $t$ y $t'$ sobre el corpus de entrada idéntico $D$, los corpus de salida $C$ son bit a bit idénticos. Esta propiedad se asegura mediante (a) la ausencia de generadores de números pseudoaleatorios o fuentes de aleatoriedad verdadera, (b) la ausencia de dependencias temporales, ambientales o de identificador de proceso, (c) orden de iteración determinístico sobre colecciones, evitando que la no determinidad de direcciones de memoria filtre al orden de serialización, y (d) la especificación determinística de `SemioticDetectorV2`. Si ejecutás el proceso repetidamente, verificás que la varianza entre salidas es exactamente cero, lo cual satisface el requisito de fiabilidad del estándar Daubert para testimonios periciales.

**6. Cumplimiento y referencias normativas**

*Estándar Daubert.* La reproducibilidad determinística del módulo, sus condiciones de error documentadas y su lógica susceptible de revisión por pares apoyan directamente los criterios de admisibilidad bajo las Federal Rules of Evidence 702, proporcionando una base fundamental para la confiabilidad científica del testimonio experto derivado de los resultados de VIGÍA.

*GB/T 22239-2019.* El módulo se adhiere a los requisitos basales de integridad de datos durante el procesamiento secundario de evidencia digital, asegurando que la transformación no introduzca alteraciones no documentadas del contenido evidencial.

*MLPS 2.0.* El hasheo de auditoría y los registros de transformación no repudiables se alinean con los requisitos del Esquema de Protección Multinivel 2.0 para el manejo forense de datos, auditoría de seguridad y trazabilidad de punta a punta.

**7. Módulos VIGÍA relacionados**

- `vigia/core/semiotic_detector_v2.py`: Suministra el motor determinístico de extracción de características $\mathcal{F}$ responsable de mapear artefactos textuales crudos hacia el espacio de características semióticas de alta dimensionalidad.
- `vigia/tools/fit_calibration.py`: Consume el corpus $C$ para estimar el mapeo de calibración $\mathcal{M}: \mathbb{R}^m \to [0,1]$, típicamente mediante escalado Platt o regresión isotónica, produciendo probabilidades posteriores $P(\text{FABRICATED} \mid \mathbf{z})$.
- `vigia_60_cases_dataset.json`: El corpus evidencial canónico anotado que sirve como dominio de entrada del módulo; su calidad de anotación impacta directamente el rendimiento de generalización del modelo de calibración posterior.

## РУССКИЙ

**Идентификатор модуля:** `vigia/tools/generate_calibration.py`

**1. Назначение модуля и системный контекст**

Модуль `generate_calibration.py` представляет собой детерминированную стадию преобразования данных в рамках судебно-экспертного конвейера VIGÍA. Его основная функция заключается в преобразовании аннотированного корпуса доказательственных материалов `vigia_60_cases_dataset.json`, содержащего шестьдесят текстовых артефактов с установленными метками истинности (ground truth), в структурированный калибровочный набор данных, пригодный для обучения вероятностных моделей. В общей архитектуре VIGÍА данный модуль располагается на границе между первичным поглощением сырых доказательств и статистическим моделированием. Он обеспечивает связь между выходными данными движка семиотической детекции и входными требованиями процедуры калибровочного согласования, гарантируя, что последующие оценки вероятности выводятся из стандартизированных, воспроизводимых векторов признаков, а не из необработанного текста.

С точки зрения судебной методологии, некалиброванный детектор выдаёт неограниченные сырые оценки, лишённые вероятностной интерпретируемости в рамках стандартов судебной допустимости. Преобразуя доказательственный корпус в векторы z-оценок, настоящий модуль обеспечивает необходимое промежуточное представление, на основе которого `fit_calibration.py` впоследствии обучает отображение из пространства признаков в вероятностный симплекс $[0,1]$. Таким образом, преобразование является не просто синтактической операцией переформатирования, но эпистемологическим предварительным условием для получения криминалистически достоверных апостериорных правдоподобий.

**2. Математические основы**

Пусть входной корпус определён как упорядоченное множество $D = \{d_1, d_2, \ldots, d_{60}\}$, где каждый элемент $d_i$ является кортежем $d_i = (t_i, y_i)$. Здесь $t_i \in \mathcal{T}$ представляет текстовый артефакт из пространства допустимых строк UTF-8, а $y_i \in \mathbb{L} = \{\text{AUTHENTIC}, \text{FABRICATED}\}$ обозначает судебно-экспертную метку истинности, присвоенную в результате независимого adjudication. Модуль реализует детерминированную функцию преобразования $\mathcal{G}: D \to C$, производя калибровочный корпус $C = \{c_1, c_2, \ldots, c_{60}\}$.

Каждая выходная запись $c_i$ формально определяется как:
$$c_i = \left(y_i, \mathbf{z}_i\right)$$
где $\mathbf{z}_i = (z_{i,1}, z_{i,2}, \ldots, z_{i,m}) \in \mathbb{R}^m$ — вектор z-оценок, извлечённый из $t_i$ по $m$ семиотическим измерениям. Для заданного измерения $k \in \mathcal{K}$ (например, $\text{SDA}$) компонента $z_{i,k}$ выводится посредством детерминированного отображения признаков $\mathcal{F}_k: \mathcal{T} \to \mathbb{R}$, инстанцированного модулем `SemioticDetectorV2`. Отображение удовлетворяет условию:
$$\forall t \in \mathcal{T}, \quad \mathcal{F}_k(t) = f_{i,k} \mapsto z_{i,k}$$
где стрелка обозначает внутренний детерминированный оператор стандартизации $\phi_k: \mathbb{R} \to \mathbb{R}$ такой, что $z_{i,k} = \phi_k(f_{i,k})$. Оператор $\phi_k$ является чистой функцией с фиксированными параметрами; он не содержит случайных величин, коэффициентов, зависящих от времени, или зависимых от среды ветвлений. Таким образом, преобразование $\mathcal{G}$ представляет собой композицию операций проверочного разбора, извлечения признаков и структурного связывания:
$$\mathcal{G} = \mathcal{B} \circ \boldsymbol{\Phi} \circ \mathcal{F}$$
где $\mathcal{F} = (\mathcal{F}_1, \ldots, \mathcal{F}_m)$ — семейство многомерных операторов извлечения признаков, $\boldsymbol{\Phi} = (\phi_1, \ldots, \phi_m)$ — семейство операторов стандартизации, а $\mathcal{B}$ — оператор связывания записей, сопоставляющий метку $y_i$ с вектором $\mathbf{z}_i$.

**3. Описание алгоритма**

Алгоритмический конвейер включает следующие строго упорядоченные стадии:

*Стадия 1 — Поглощение и валидация схемы.* Модуль считывает файл `vigia_60_cases_dataset.json` и проверяет, что каждая запись содержит ненулевое текстовое поле и метку истинности из множества $\mathbb{L}$. Любая запись, нарушающая схему, инициирует детерминированное фатальное исключение, останавливающее выполнение для предотвращения загрязнения калибровочных данных. Данный этап валидации обеспечивает замкнутость домена над входным множеством и служит предпосылкой для всех последующих математических преобразований.

*Стадия 2 — Детерминированное извлечение признаков.* Для каждого проверенного артефакта $t_i$ модуль вызывает `SemioticDetectorV2.compute(text=t_i)`. Данный движок применяет детерминированный анализ, основанный на правилах и статистических основаниях, для вывода сырых значений семиотических признаков $f_{i,k}$ по каждому измерению $k \in \mathcal{K}$. Процесс полностью нестохастичен; не используются случайная выборка, оценки методом Монте-Карло или вероятностные возмущения. Следовательно, для фиксированного входа $t_i$ оператор извлечения признаков $\mathcal{F}$ выдаёт постоянный вектор при любом запуске.

*Стадия 3 — Стандартизация z-оценок.* Сырые признаки преобразуются в z-оценки с использованием фиксированных внутренних параметров и предварительно вычисленных описательных статистик совокупности, встроенных в `SemioticDetectorV2`. Для каждого измерения $k$ оператор стандартизации $\phi_k$ отображает $f_{i,k}$ в $z_{i,k}$ в соответствии с детерминированным набором правил детектора. Это гарантирует, что $z_{i,k}$ представляет собой фиксированную, сопоставимую меру отклонения от референтного распределения детектора, устраняя размерные различия, которые в противном случае искажали бы последующее калибровочное согласование.

*Стадия 4 — Структурирование записей.* Модуль связывает каждую метку истинности $y_i$ с соответствующей картой z-оценок для формирования записи $c_i$. Выходная схема обеспечивает биективное отображение между входным индексом $i$ и выходным индексом, сохраняя доказательственный порядок и гарантируя отсутствие дублирования или пропуска записей при передаче.

*Стадия 5 — Сериализация.* Калибровочный корпус $C$ сериализуется в поток байтов, совместимый с JSON. Числовые представления обрабатываются по детерминированным правилам форматирования, обеспечивая побитовую согласованность между запусками на идентичных программно-аппаратных комплексах и удовлетворяя строгим требованиям воспроизводимости, предъявляемым к судебной обработке данных.

*Стадия 6 — Аудиторское хеширование.* Вычисляется криптографический дайджест (SHA-256) как входного, так и выходного корпуса для установления базовой линии целостности при документировании цепочки сохранения. Данный дайджест служит якорем для аудиторских следов на уровне модуля и поддерживает невозможную для отказа верификацию всего преобразования.

**4. Спецификации входных и выходных данных**

*Вход:* файл `vigia_60_cases_dataset.json`; кодировка UTF-8; схема в виде массива объектов с ключами `text` (строка) и `label` (перечисление $\mathbb{L}$). Каноническая мощность $|D| = 60$.

*Выход:* файл калибровочных векторов; схема в виде массива объектов с ключами `ground_truth` (перечисление $\mathbb{L}$) и `z_scores` (объект, отображающий идентификаторы измерений, такие как `SDA`, на вещественные скаляры). Выход функционально типизирован как $C \subset \mathbb{L} \times \mathbb{R}^m$.

**5. Детерминированные гарантии**

Модуль обеспечивает строгие детерминированные гарантии, критически важные для судебной допустимости. Формально:
$$\forall t, t' \in \text{Exec}, \quad \mathcal{G}(D)_t = \mathcal{G}(D)_{t'}$$
то есть для любых двух запусков $t$ и $t'$ на идентичном входном корпусе $D$ выходные корпуса $C$ побитово идентичны. Данное свойство обеспечивается: (a) отсутствием генераторов псевдослучайных чисел или источников истинной случайности, (b) отсутствием временных, контекстных или процессно-зависимых зависимостей, (c) детерминированным порядком итерации по коллекциям, предотвращающим утечку недетерминированности адресов памяти в порядок сериализации, (d) детерминированной спецификацией `SemioticDetectorV2`. Эти гарантии удовлетворяют требованию надёжности стандарта Daubert для экспертных свидетельских показаний, поскольку устанавливают известную процедуру с нулевой дисперсией при идентичных условиях.

**6. Соответствие стандартам и нормативные ссылки**

*Стандарт Daubert.* Детерминированная воспроизводимость модуля, документированные условия возникновения ошибок и логика, доступная для рецензирования, непосредственно поддерживают критерии допустимости в соответствии с Federal Rules of Evidence 702, обеспечивая основу для научной надёжности экспертных заключений, выводимых из результатов VIGÍA.

*GB/T 22239-2019.* Модуль соблюдает базовые требования к целостности данных при вторичной обработке цифровых доказательств, гарантируя отсутствие внесения незадокументированных изменений в содержание доказательственных материалов.

*MLPS 2.0.* Аудиторское хеширование и невозможные для отказа журналы преобразований соответствуют требованиям многоуровневой схемы защиты 2.0 (Multi-Level Protection Scheme 2.0) к судебно-экспертной обработке данных, аудиту безопасности и сквозной прослеживаемости.

**7. Связанные модули VIGÍA**

- `vigia/core/semiotic_detector_v2.py`: поставляет детерминированный движок извлечения признаков $\mathcal{F}$, отвечающий за отображение сырых текстовых артефактов в многомерное семиотическое пространство признаков.
- `vigia/tools/fit_calibration.py`: потребляет корпус $C$ для оценки калибровочного отображения $\mathcal{M}: \mathbb{R}^m \to [0,1]$, как правило, посредством масштабирования Платта или изотонической регрессии, формируя апостериорные вероятности $P(\text{FABRICATED} \mid \mathbf{z})$.
- `vigia_60_cases_dataset.json`: канонический аннотированный доказательственный корпус, служащий входным доменом модуля; качество его разметки непосредственно влияет на обобщающую способность последующей калибровочной модели.

## 中文

**模块标识符：** `vigia/tools/generate_calibration.py`

**1. 模块目的与系统上下文**

本模块作为 VIGÍA 司法鉴定流水线中的确定性数据转换环节，其核心功能是将已标注的证据语料库 `vigia_60_cases_dataset.json`（包含六十件具备既定真实性基准标签的文本证物）转换为适用于概率模型训练的结构化校准数据集。在 VIGÍA 整体架构内，该模块位于原始证物摄取与统计模型拟合之间的边界层。它在符号检测引擎的输出端与校准拟合过程的输入需求之间建立确定性桥梁，确保下游概率估计源于标准化且可复现的特征向量，而非未经处理的原始文本。

从司法鉴定方法论角度审视，未经校准的检测器仅输出无界原始分数，缺乏概率解释力；而本模块生成的 z-score 向量经过标准化处理，为后续 `fit_calibration.py` 将特征空间映射至概率空间 $[0,1]$ 提供必要条件。因此，该转换并非单纯的语法重格式化操作，而是生成司法上有效的后验似然的认识论前提。

**2. 数学基础**

设输入语料库为有序集合 $D = \{d_1, d_2, \ldots, d_{60}\}$，其中每个元素 $d_i$ 构成二元组 $d_i = (t_i, y_i)$。此处 $t_i \in \mathcal{T}$ 表示取自可接受 UTF-8 字符串空间的文本证物；$y_i \in \mathbb{L} = \{\text{AUTHENTIC}, \text{FABRICATED}\}$ 表示经由独立裁决程序赋予的真实性基准标签。本模块实现确定性变换函数 $\mathcal{G}: D \to C$，生成校准语料库 $C = \{c_1, c_2, \ldots, c_{60}\}$。

每条输出记录 $c_i$ 的形式化定义为：
$$c_i = \left(y_i, \mathbf{z}_i\right)$$
其中 $\mathbf{z}_i = (z_{i,1}, z_{i,2}, \ldots, z_{i,m}) \in \mathbb{R}^m$ 为自 $t_i$ 提取的跨 $m$ 个符号学维度的 z-score 向量。对于给定维度 $k \in \mathcal{K}$（例如 $\text{SDA}$），分量 $z_{i,k}$ 经由 `SemioticDetectorV2` 实例化的确定性特征映射 $\mathcal{F}_k: \mathcal{T} \to \mathbb{R}$ 导出。该映射满足关系：
$$\forall t \in \mathcal{T}, \quad \mathcal{F}_k(t) = f_{i,k} \mapsto z_{i,k}$$
式中箭头表示内部确定性标准化算子 $\phi_k: \mathbb{R} \to \mathbb{R}$，使得 $z_{i,k} = \phi_k(f_{i,k})$。此处 $\phi_k$ 为具有固定参数的纯函数，不包含任何随机变量、时变系数或环境依赖分支。因此，整体变换 $\mathcal{G}$ 可视为经验证的解析、特征提取与结构绑定操作的复合函数：
$$\mathcal{G} = \mathcal{B} \circ \boldsymbol{\Phi} \circ \mathcal{F}$$
其中 $\mathcal{F} = (\mathcal{F}_1, \ldots, \mathcal{F}_m)$ 为多维特征提取算子族，$\boldsymbol{\Phi} = (\phi_1, \ldots, \phi_m)$ 为标准化算子族，$\mathcal{B}$ 为记录绑定算子，负责将标签 $y_i$ 与向量 $\mathbf{z}_i$ 组合为结构化记录。

**3. 算法描述**

算法流水线由以下严格有序的阶段构成：

*阶段 1——摄取与模式校验。* 模块读取 `vigia_60_cases_dataset.json`，并校验每条记录均包含非空文本字段及属于集合 $\mathbb{L}$ 的真实性基准标签。任何违反模式的记录均触发确定性致命异常，立即中断执行以防止校准数据集受到污染。该校验机制确保输入域的封闭性，是后续数学变换有效性的前提条件。

*阶段 2——确定性特征提取。* 对于每件通过校验的证物 $t_i$，模块调用 `SemioticDetectorV2.compute(text=t_i)`。该引擎应用基于规则且具备统计学基础的确定性分析，以导出每个维度 $k \in \mathcal{K}$ 的原始符号学特征值 $f_{i,k}$。该过程完全非随机；不采用随机采样、蒙特卡洛估计或概率扰动。因此，对于固定输入 $t_i$，特征提取算子 $\mathcal{F}$ 的输出始终为常向量。

*阶段 3——z-score 标准化。* 原始特征依据 `SemioticDetectorV2` 内嵌的固定参数与预计算总体统计量转换为 z-score。对于每个维度 $k$，标准化算子 $\phi_k$ 按照检测器确定性规则集将 $f_{i,k}$ 映射为 $z_{i,k}$。该步骤确保 $z_{i,k}$ 表示相对于检测器参考分布的固定、可比偏离度量，消除量纲差异对后续校准拟合的干扰。

*阶段 4——记录结构化。* 模块将每条真实性基准标签 $y_i$ 与其对应的 z-score 映射 $\mathbf{z}_i$ 绑定，以形成输出记录 $c_i$。输出模式强制输入索引 $i$ 与输出索引之间保持双射关系，严格保全原始证据的时序与逻辑顺序，杜绝传输过程中的重复或遗漏。

*阶段 5——序列化。* 校准语料库 $C$ 被序列化为符合 JSON 规范的字节流。数值表示通过确定性格式化规则处理，确保在相同软硬件栈上的多次执行之间实现位级一致，满足司法鉴定对数据再现性的严苛要求。

*阶段 6——审计哈希。* 对输入语料库与输出语料库分别计算密码学摘要（SHA-256），为保管链文档建立不可篡改的完整性基线。该哈希值作为模块级审计追踪的锚点，支持对整个转换过程的非否认性验证。

**4. 输入/输出规范**

*输入：* 文件 `vigia_60_cases_dataset.json`；编码 UTF-8；模式为对象数组，每条对象至少包含键 `text`（字符串类型）与 `label`（枚举型，取值域为 $\mathbb{L}$）。标准基数 $|D| = 60$。

*输出：* 校准向量文件；模式为对象数组，每条对象包含键 `ground_truth`（枚举型 $\mathbb{L}$）与 `z_scores`（对象类型，其键为维度标识符如 `SDA`，值为实值标量）。输出在功能类型上可形式化为 $C \subset \mathbb{L} \times \mathbb{R}^m$。

**5. 确定性保证**

本模块提供对司法可采性至关重要的严格确定性保证。形式化表述为：
$$\forall t, t' \in \text{Exec}, \quad \mathcal{G}(D)_t = \mathcal{G}(D)_{t'}$$
即对于同一输入语料库 $D$ 的任意两次执行 $t$ 与 $t'$，输出语料库 $C$ 位级相同。该性质通过以下机制得以严格保障：(a) 不含伪随机数生成器或真随机数源；(b) 不含时间戳、进程标识符等环境依赖；(c) 对集合采用确定性迭代顺序，杜绝由内存地址非确定性引入的次序差异；(d) `SemioticDetectorV2` 的算法规范本身为纯确定性函数。上述保证满足道伯特标准（Daubert）对专家证言可靠性的核心要求——程序在相同条件下的误差率为零且完全可复现。

**6. 合规性与标准引用**

*道伯特标准（Daubert）。* 本模块的确定性可复现性、已文档化的错误条件以及可供同行评审的逻辑架构，直接支持《联邦证据规则》702 条下的可采性审查标准，为专家证言的科学可靠性提供基础。

*GB/T 22239-2019（信息安全技术 网络安全等级保护基本要求）。* 本模块遵守数字证据二次处理过程中的数据完整性基线要求，确保转换环节不引入未记录的数据变更。

*MLPS 2.0（网络安全等级保护制度 2.0）。* 审计哈希与不可抵赖的转换日志符合 MLPS 2.0 对取证数据处理、安全审计与全过程可追溯性的合规要求。

**7. 相关 VIGÍA 模块**

- `vigia/core/semiotic_detector_v2.py`：提供确定性特征提取引擎 $\mathcal{F}$，负责将原始文本证物映射至高维符号学特征空间。
- `vigia/tools/fit_calibration.py`：消费本模块输出的语料库 $C$，用于估计校准映射 $\mathcal{M}: \mathbb{R}^m \to [0,1]$。该过程通常采用 Platt 缩放或保序回归（isotonic regression），最终生成后验概率 $P(\text{FABRICATED} \mid \mathbf{z})$。
- `vigia_60_cases_dataset.json`：作为本模块输入域的标准基准证据语料库，其标注质量直接影响下游校准模型的泛化性能。