## ENGLISH

**Module Designation:** `vigia.sift.sans_phase` — Phase-Invariant Deterministic Preprocessing Subcomponent

**1. Module Purpose and Forensic Rationale**

The module `vigia.sift.sans_phase` constitutes a mandatory preprocessing stage within the VIGÍA digital-forensics architecture, specifically situated in the `vigia.sift` feature-extraction submodule. Its primary function is to perform deterministic, bitwise-reproducible normalization of evidentiary media by abstracting phase-invariant signal characteristics through strictly discrete integer transforms. In forensic practice, the chain-of-custody and admissibility of digital evidence demand that analytical derivatives—feature descriptors, hash inputs, and similarity metrics—remain invariant across computational environments. Conventional preprocessing pipelines frequently invoke floating-point fast Fourier transforms (FFT), trigonometric phase extractions, and hardware-optimized SIMD approximations that introduce platform-dependent rounding errors, non-deterministic branch scheduling, and library-version discrepancies. `sans_phase.py` eliminates these vectors of variance by confining all internal operations to integer arithmetic, pre-computed transcendental constants, and explicit modular reduction, thereby yielding descriptors that are bit-exact on x86_64, AArch64, and RISC-V platforms. This deterministic property directly supports Daubert criteria for scientific evidence by furnishing a testable, peer-reviewed methodology with a bounded and known algorithmic error rate—effectively zero variance for a fixed input—and by ensuring that downstream analytical modules receive standardized, phase-agnostic feature representations.

**2. Mathematical Foundations**

Let the input evidentiary signal be represented as a discrete raster $\mathbf{s} \in \mathbb{Z}^{H \times W \times C}$, where $H$ and $W$ denote spatial dimensions and $C \in \{1, 3, 4\}$ denotes the number of channels after canonicalization by the upstream ingestion layer. Each sample is quantized to a fixed bit-depth $B$ (typically $B=16$) as an unsigned integer. The module partitions $\mathbf{s}$ into non-overlapping or optionally overlapping tiles $\mathbf{b}_{i,j} \in \mathbb{Z}^{N \times N}$ indexed by $(i,j)$.

The core transformation relies on a separable integer basis matrix $\mathbf{T} \in \mathbb{Z}^{N \times N}$ that approximates the discrete Fourier transform (DFT) or discrete cosine transform (DCT) kernel without invoking transcendental functions at runtime. The entries of $\mathbf{T}$ are pre-computed as scaled integers:

$$
T_{u,m} = \left\lfloor K \cdot \cos\left(\frac{2\pi u m}{N}\right) + \frac{1}{2} \right\rfloor, \quad K = 2^{20}
$$

for the cosine component, with an analogous sine component where the transform requires complex representation. The scaling factor $K$ is global and invariant, ensuring that all basis values are compile-time constants stored as immutable integers within the module namespace.

The forward discrete integer transform (FDIT) on a tile $\mathbf{b}$ is defined separably. First, row-wise transformation produces an intermediate matrix $\mathbf{M}$:

$$
M_{u,n} = \sum_{m=0}^{N-1} b_{m,n} \cdot T_{u,m}
$$

followed by column-wise transformation to yield the spectrum coefficients:

$$
\hat{b}_{u,v} = \sum_{n=0}^{N-1} M_{u,n} \cdot T_{v,n}
$$

All summations are performed using 128-bit intermediate accumulators (emulated via explicit bitmasking in Python) to prevent overflow; the final result is reduced to a 64-bit signed integer range via explicit two's-complement masking, eliminating undefined behavior dependencies on compiler or CPU architecture.

Phase invariance is enforced by computing the squared modulus of complex-valued integer pairs. If the transform produces a real part $\Re_{u,v}$ and an imaginary part $\Im_{u,v}$, the phase-invariant power-spectrum coefficient is:

$$
P_{u,v} = \Re_{u,v}^2 + \Im_{u,v}^2
$$

This operation discards the phase angle $\phi_{u,v} = \arctan2(\Im_{u,v}, \Re_{u,v})$ without requiring any floating-point inverse trigonometric evaluation. For strictly real integer transforms (e.g., integer DCT approximations), phase abstraction is implicit in the coefficient magnitude. The resulting coefficients are quantized to a fixed-point descriptor via a uniform scalar divisor:

$$
d_{u,v} = \left\lfloor \frac{P_{u,v}}{2^q} \right\rfloor
$$

where $q$ is a pipeline-global fixed-point parameter (default $q=10$). The division is implemented as an arithmetic right bit-shift, guaranteeing a single, unambiguous rounding mode (round-toward-negative-infinity for positive integers).

**3. Algorithmic Description**

The operational pipeline of `sans_phase.py` comprises six deterministic stages:

*Stage 1 — Canonical Ingestion.* The module accepts raw evidentiary buffers from `vigia.io.ingest`, which provides media decoded into a canonical integer raster. If color-space conversion is required (e.g., YCbCr or grayscale reduction), the module utilizes exact integer coefficient matrices conforming to ITU-R BT.601/BT.709 integer approximations, precluding floating-point color resampling.

*Stage 2 — Tiling and Boundary Conditioning.* The raster is tessellated into $N \times N$ tiles. Boundary tiles that extend beyond the image extent are subjected to deterministic reflective padding (index mirroring computed by integer arithmetic) or zero-padding, as configured by the pipeline policy. The padding logic contains no conditional branches dependent on uninitialized memory.

*Stage 3 — Forward Discrete Integer Transform.* Each tile undergoes the separable FDIT. The implementation iterates over indices in fixed nested loops, using only integer addition, subtraction, and multiplication. The transform kernel constants are loaded from an immutable module-level tuple, ensuring that every execution employs identical basis values.

*Stage 4 — Phase Nullification.* For each transformed tile, the module computes $P_{u,v}$ from complex integer pairs or extracts magnitude from real coefficients. This stage collapses the phase dimension, yielding a representation invariant under the Fourier shift theorem; spatial or temporal translations of the input affect only phase, leaving $P_{u,v}$ unchanged.

*Stage 5 — Fixed-Point Quantization.* The power-spectrum values are quantized via the specified arithmetic right-shift. The output of this stage is an array of integers of predetermined width, suitable for direct hashing or comparison.

*Stage 6 — Canonical Serialization.* The resulting descriptor tiles are serialized in big-endian byte order according to the VIGÍA Canonical Byte Format (VCBF). Each `SansPhaseDescriptor` record encodes the tile coordinates $(i,j)$, the quantized spectrum $\mathbf{d}$, and an optional cumulative integrity checksum if Merkle-tree sealing is enabled by `vigia.hash.merkle`.

**4. Input and Output Specifications**

*Input.* The public interface `process(evidence_stream: Union[bytes, mmap, VigiaRaster]) -> SansPhaseDescriptorStream` accepts raw byte sequences, memory-mapped forensic images, or pre-canonicalized raster objects. The module assumes that upstream ingestion has normalized bit-depth and color space; however, it defensively validates that all input samples are integers within the expected domain.

*Output.* The module emits a deterministic stream of `SansPhaseDescriptor` records. Internally, all arithmetic employs Python’s arbitrary-precision `int` type, yet the implementation explicitly masks to 64-bit or 128-bit at operation boundaries to simulate fixed-width ALU behavior. This architectural choice guarantees that the serialized byte output is identical regardless of the host Python interpreter’s internal big-integer representation or the underlying processor word size.

**5. Deterministic Guarantees and Chain-of-Custody Compliance**

The forensic validity of `sans_phase.py` rests on five deterministic guarantees. First, **Bit-Exact Reproducibility (BER):** for any fixed input, the output byte sequence is identical across all supported architectures, as certified by the regression suite in `vigia.verify.determinism`. Second, **No Floating-Point Contamination:** the module contains no invocations of `float`, `math.sin`, `math.cos`, `numpy.float64`, or hardware FPU approximations. Third, **Defined Overflow Semantics:** integer wraparound follows explicit two’s-complement masking (`& 0xFFFFFFFFFFFFFFFF`), removing undefined behavior variance. Fourth, **Memory Layout Independence:** canonical big-endian serialization and explicit struct packing remove endianness dependencies. Fifth, **Temporal Stability:** the output is invariant to thread-scheduling fluctuations, garbage-collection pauses, and I/O latency because tile processing is stateless and stream ordering is fixed by input geometry.

These properties preserve chain-of-custody requirements by ensuring that derived descriptors can be re-generated at any future date with identical results, allowing forensic examiners to demonstrate that analytical artifacts have not been altered by toolchain drift.

**6. Integration with Related VIGÍA Modules**

The module registers with `vigia.sift.core` as a mandatory preprocessing stage in the feature-extraction pipeline. Its output feeds directly into `vigia.sift.keypoint`, which performs scale-space extrema detection on the phase-invariant descriptors. Integrity verification is handled by `vigia.hash.merkle`, which seals each descriptor block into a tamper-evident cryptographic tree. Provenance metadata—including module version, transform parameters $(N, K, q)$, and execution timestamp—is appended by `vigia.pipeline.custody` to the evidentiary audit log. Cross-platform deterministic certification is continuously enforced by `vigia.verify.determinism`.

**7. Standardization and Admissibility Criteria**

Under the **Daubert** standard, the methodology is falsifiable (via bitwise differential analysis), subjected to peer review through documented open-kernel constants, and exhibits a known error rate that is algorithmically zero for repeated execution. The module aligns with **GB/T 29360** (electronic data forensic examination methods) and **GB/T 31500** (big-data reference architecture) by guaranteeing data integrity, process traceability, and reproducibility of forensic derivatives. Furthermore, it satisfies **MLPS 2.0** (Multi-Level Protection Scheme 2.0) requirements by ensuring that processing within classified or controlled environments produces non-repudiable, auditable descriptors without introducing floating-point side channels or non-deterministic approximations.

---

## ESPAÑOL

**Designación del módulo:** `vigia.sift.sans_phase` — Subcomponente determinista de preprocesamiento invariante de fase

**1. Propósito del módulo y fundamentación forense**

El presente módulo, identificado como `vigia.sift.sans_phase`, se emplaza como una etapa obligatoria de preprocesamiento dentro de la arquitectura de informática forense VIGÍA, en particular al interior del submódulo de extracción de características `vigia.sift`. Su función principal consiste en efectuar la normalización determinista y reproducible a nivel de bit de medios probatorios mediante la abstracción de características invariantes de fase a través de transformaciones enteras discretas exclusivamente. En la práctica forense, la cadena de custodia y la admisibilidad de la evidencia digital exigen que los derivados analíticos —descriptores de rasgos, insumos para funciones de hash y métricas de similitud— se mantengan invariantes frente a modificaciones del entorno computacional. Los pipelines convencionales de preprocesamiento suelen invocar transformadas rápidas de Fourier (FFT) de punto flotante, extracciones trigonométricas de fase y aproximaciones SIMD optimizadas por hardware que introducen errores de redondeo dependientes de la plataforma, bifurcaciones de ejecución no deterministas y discrepancias vinculadas a versiones de bibliotecas. El archivo `sans_phase.py` elimina dichos vectores de varianza al restringir todas sus operaciones internas a la aritmética de enteros, constantes trascendentales precomputadas y reducción modular explícita, generando descriptores bit a bit idénticos en arquitecturas x86_64, AArch64 y RISC-V. Esta propiedad determinista respalda directamente los criterios del estándar Daubert para evidencia científica, ya que provee una metodología testeable, sometida a revisión por pares y con una tasa de error algorítmica acotada —cero varianza para una entrada fija—, garantizando al mismo tiempo que los módulos analíticos aguas abajo reciban representaciones estandarizadas y agnósticas de la fase.

**2. Fundamentos matemáticos**

Sea la señal de entrada probatoria representada como un raster discreto $\mathbf{s} \in \mathbb{Z}^{H \times W \times C}$, donde $H$ y $W$ indican las dimensiones espaciales y $C \in \{1, 3, 4\}$ la cantidad de canales luego de la canonicalización efectuada por la capa de ingestión superior. Cada muestra se cuantiza a una profundidad de bit fija $B$ (típicamente $B=16$) como entero sin signo. El módulo particiona $\mathbf{s}$ en teselas $\mathbf{b}_{i,j} \in \mathbb{Z}^{N \times N}$, indexadas por $(i,j)$, que pueden ser no solapadas o solapadas según la política del pipeline.

La transformación central se apoya en una matriz base entera separable $\mathbf{T} \in \mathbb{Z}^{N \times N}$ que aproxima el núcleo de la transformada discreta de Fourier (DFT) o de la transformada discreta de cosenos (DCT) sin invocar funciones trascendentales en tiempo de ejecución. Los elementos de $\mathbf{T}$ se precomputan como enteros escalados:

$$
T_{u,m} = \left\lfloor K \cdot \cos\left(\frac{2\pi u m}{N}\right) + \frac{1}{2} \right\rfloor, \quad K = 2^{20}
$$

para el componente coseno, con un componente seno análogo cuando la transformación requiere representación compleja. El factor de escala $K$ es global e invariable, de modo que todos los valores base son constantes de tiempo de compilación almacenadas como enteros inmutables en el espacio de nombres del módulo.

La transformada entera discreta directa (FDIT) sobre una tesela $\mathbf{b}$ se define de forma separable. Primero, la transformación por filas produce una matriz intermedia $\mathbf{M}$:

$$
M_{u,n} = \sum_{m=0}^{N-1} b_{m,n} \cdot T_{u,m}
$$

y luego la transformación por columnas arroja los coeficientes espectrales:

$$
\hat{b}_{u,v} = \sum_{n=0}^{N-1} M_{u,n} \cdot T_{v,n}
$$

Todas las sumatorias se ejecutan utilizando acumuladores intermedios de 128 bits (emulados mediante enmascaramiento explícito en Python) para prevenir desbordamiento; el resultado final se reduce a un rango de enteros signados de 64 bits mediante enmascaramiento explícito en complemento a dos, eliminando dependencias de comportamiento indefinido vinculadas al compilador o a la arquitectura del CPU.

La invarianza de fase se impone computando el módulo cuadrado de pares enteros complejos. Si la transformada produce una parte real $\Re_{u,v}$ y una parte imaginaria $\Im_{u,v}$, el coeficiente del espectro de potencia invariante a la fase resulta:

$$
P_{u,v} = \Re_{u,v}^2 + \Im_{u,v}^2
$$

Esta operación descarta el ángulo de fase $\phi_{u,v} = \arctan2(\Im_{u,v}, \Re_{u,v})$ sin requerir evaluación trigonométrica inversa de punto flotante. Para transformaciones enteras estrictamente reales (por ejemplo, aproximaciones enteras de la DCT), la abstracción de fase es implícita en la magnitud de los coeficientes. Los coeficientes resultantes se cuantizan a un descriptor de punto fijo mediante un divisor escalar uniforme:

$$
d_{u,v} = \left\lfloor \frac{P_{u,v}}{2^q} \right\rfloor
$$

donde $q$ es un parámetro de punto fijo global del pipeline (valor predeterminado $q=10$). La división se implementa como un desplazamiento aritmético a derecha, garantizando un único modo de redondeo inequívoco (redondeo hacia menos infinito para enteros positivos).

**3. Descripción algorítmica**

El pipeline operativo de `sans_phase.py` comprende seis etapas deterministas:

*Etapa 1 — Ingesta canónica.* El módulo acepta búferes probatorios crudos provenientes de `vigia.io.ingest`, que provee los medios decodificados en un raster entero canónico. Si se requiere conversión de espacio de color (por ejemplo, reducción a YCbCr o escala de grises), el módulo utiliza matrices de coeficientes enteros exactos conformes a las aproximaciones enteras ITU-R BT.601/BT.709, evitando el remuestreo de color en punto flotante.

*Etapa 2 — Teselado y acondicionamiento de bordes.* El raster se tesela en bloques de $N \times N$. Las teselas de borde que exceden la extensión de la imagen se someten a relleno reflectivo determinista (cálculo de índices espejados mediante aritmética entera) o relleno de ceros, según la política configurada del pipeline. La lógica de relleno no contiene bifurcaciones condicionales dependientes de memoria no inicializada.

*Etapa 3 — Transformada entera discreta directa.* Cada tesela se somete a la FDIT separable. La implementación itera sobre índices en lazos anidados fijos, empleando únicamente suma, resta y multiplicación de enteros. Las constantes del núcleo transformado se cargan desde una tupla inmutable a nivel de módulo, asegurando que cada ejecución utilice valores base idénticos.

*Etapa 4 — Anulación de fase.* Para cada tesela transformada, el módulo computa $P_{u,v}$ a partir de pares enteros complejos o extrae la magnitud de coeficientes reales. Esta etapa colapsa la dimensión de fase, produciendo una representación invariante bajo el teorema de desplazamiento de Fourier; las traslaciones espaciales o temporales de la entrada afectan únicamente la fase, dejando $P_{u,v}$ inalterado.

*Etapa 5 — Cuantización de punto fijo.* Los valores del espectro de potencia se cuantizan mediante el desplazamiento aritmético a derecha especificado. La salida de esta etapa es un arreglo de enteros de ancho predeterminado, apto para hash o comparación directa.

*Etapa 6 — Serialización canónica.* Los descriptores teselados resultantes se serializan en orden de bytes big-endian conforme al Formato de Bytes Canónico VIGÍA (VCBF). Cada registro `SansPhaseDescriptor` codifica las coordenadas de tesela $(i,j)$, el espectro cuantizado $\mathbf{d}$ y una suma de verificación acumulativa opcional si el sellado por árbol de Merkle está habilitado mediante `vigia.hash.merkle`.

**4. Especificaciones de entrada y salida**

*Entrada.* La interfaz pública `process(evidence_stream: Union[bytes, mmap, VigiaRaster]) -> SansPhaseDescriptorStream` acepta secuencias de bytes crudos, imágenes forenses mapeadas en memoria u objetos raster precanonicalizados. El módulo asume que la ingestión superior normalizó la profundidad de bit y el espacio de color; no obstante, valida defensivamente que todas las muestras de entrada sean enteros dentro del dominio esperado.

*Salida.* El módulo emite un flujo determinista de registros `SansPhaseDescriptor`. Internamente, toda la aritmética emplea el tipo `int` de precisión arbitraria de Python, aunque la implementación enmascara explícitamente a 64 o 128 bits en los límites de cada operación para emular el comportamiento de una ALU de ancho fijo. Esta elección arquitectónica garantiza que la secuencia de bytes serializada sea idéntica independientemente de la representación interna de enteros grandes del intérprete Python o del tamaño de palabra del procesador subyacente.

**5. Garantías deterministas y cumplimiento de la cadena de custodia**

La validez forense de `sans_phase.py` se asienta sobre cinco garantías deterministas. Primera, **reproducibilidad bit a bit (BER):** para una entrada fija, la secuencia de bytes de salida es idéntica en todas las arquitecturas soportadas, según certifica la suite de regresión de `vigia.verify.determinism`. Segunda, **ausencia de contaminación de punto flotante:** el módulo no contiene invocaciones de `float`, `math.sin`, `math.cos`, `numpy.float64` ni aproximaciones de FPU hardware. Tercera, **semántica definida de desbordamiento:** el desbordamiento entero sigue un enmascaramiento explícito en complemento a dos (`& 0xFFFFFFFFFFFFFFFF`), eliminando varianzas por comportamiento indefinido. Cuarta, **independencia del layout de memoria:** la serialización canónica big-endian y el empaquetado estructurado explícito remueven dependencias de endianness. Quinta, **estabilidad temporal:** la salida es invariante ante fluctuaciones de planificación de hilos, pausas del recolector de basura y latencias de E/S, dado que el procesamiento de teselas es sin estado y el orden del flujo se fija por la geometría de entrada.

Si vos ejecutás una auditoría de reproducibilidad, observarás que estas propiedades preservan los requisitos de cadena de custodia al asegurar que los descriptores derivados puedan regenerarse en cualquier fecha futura con resultados idénticos, permitiéndole al perito forense demostrar que los artefactos analíticos no fueron alterados por derivas en la cadena de herramientas.

**6. Integración con módulos VIGÍA relacionados**

El módulo se registra en `vigia.sift.core` como una etapa obligatoria del pipeline de extracción de características. Su salida alimenta directamente a `vigia.sift.keypoint`, que realiza la detección de extremos en espacio de escala sobre los descriptores invariantes de fase. La verificación de integridad está a cargo de `vigia.hash.merkle`, que sella cada bloque descriptor en un árbol criptográfico anti-manipulación. Los metadatos de procedencia —incluyendo versión del módulo, parámetros de transformada $(N, K, q)$ y marca temporal de ejecución— son agregados por `vigia.pipeline.custody` al registro de auditoría probatoria. La certificación determinista multiplataforma se refuerza continuamente mediante `vigia.verify.determinism`.

**7. Criterios de estandarización y admisibilidad**

Bajo el estándar **Daubert**, la metodología es refutable (mediante análisis diferencial bit a bit), sometida a revisión por pares a través de constantes de núcleo abiertas documentadas, y exhibe una tasa de error conocida que es algorítmicamente cero para ejecuciones repetidas. El módulo se alinea con la norma **GB/T 29360** (métodos de examen forense de datos electrónicos) y con **GB/T 31500** (arquitectura de referencia de big data) al garantizar integridad de datos, trazabilidad del proceso y reproducibilidad de derivados forenses. Además, satisface los requisitos del esquema **MLPS 2.0** (Multi-Level Protection Scheme 2.0) al asegurar que el procesamiento en entornos clasificados o controlados produzca descriptores no repudiables y auditables sin introducir canales laterales de punto flotante ni aproximaciones no deterministas.

---

## РУССКИЙ

**Наименование модуля:** `vigia.sift.sans_phase` — Детерминированный подкомпонент предобработки, инвариантный к фазе

**1. Назначение модуля и судебная обоснованность**

Настоящий модуль `vigia.sift.sans_phase` представляет собой обязательную стадию предобработки в архитектуре цифровой криминалистики VIGÍA, конкретно в составе подмодуля извлечения признаков `vigia.sift`. Его основная функция заключается в выполнении детерминированной, побитово воспроизводимой нормализации доказательственных носителей путём абстрагирования фазо-инвариантных характеристик сигнала исключительно посредством дискретных целочисленных преобразований. В криминалистической практике сохранение цепочки сохранности и допустимость цифровых доказательств требуют, чтобы аналитические производные — дескрипторы признаков, входные данные для хеш-функций и метрики сходства — оставались инвариантными по отношению к вычислительной среде. Традиционные конвейеры предобработки нередко задействуют преобразования Фурье с плавающей точкой (FFT), тригонометрическое извлечение фазы и аппаратно-оптимизированные SIMD-аппроксимации, вносящие зависимые от платформы ошибки округления, недетерминированное ветвление и расхождения, обусловленные версиями библиотек. Модуль `sans_phase.py` устраняет указанные источники дисперсии, ограничивая все внутренние операции целочисленной арифметикой, предвычисленными трансцендентными константами и явной модульной редукцией, в результате чего формируются дескрипторы, побитово идентичные на архитектурах x86_64, AArch64 и RISC-V. Указанное свойство детерминизма непосредственно поддерживает критерии стандарта Daubert для научных доказательств, обеспечивая тестируемую, рецензируемую методологию с известной, строго ограниченной частотой ошибок — алгоритмически нулевой дисперсией при фиксированном входе — и гарантируя, что нисходящие аналитические модули получают стандартизированные фазово-агностические представления.

**2. Математические основы**

Пусть входной доказательственный сигнал представлен в виде дискретного растра $\mathbf{s} \in \mathbb{Z}^{H \times W \times C}$, где $H$ и $W$ обозначают пространственные размерности, а $C \in \{1, 3, 4\}$ — число каналов после канонизации, выполняемой восходящим уровнем загрузки. Каждый отсчёт квантуется с фиксированной разрядностью $B$ (обычно $B=16$) в виде целого числа без знака. Модуль разбивает $\mathbf{s}$ на неперекрывающиеся или опционально перекрывающиеся плитки $\mathbf{b}_{i,j} \in \mathbb{Z}^{N \times N}$ с индексами $(i,j)$.

Базовое преобразование опирается на сепарабельную целочисленную базисную матрицу $\mathbf{T} \in \mathbb{Z}^{N \times N}$, аппроксимирующую ядро дискретного преобразования Фурье (ДПФ) или дискретного косинусного преобразования (ДКП) без вызова трансцендентных функций во время выполнения. Элементы $\mathbf{T}$ предвычисляются как масштабированные целые числа:

$$
T_{u,m} = \left\lfloor K \cdot \cos\left(\frac{2\pi u m}{N}\right) + \frac{1}{2} \right\rfloor, \quad K = 2^{20}
$$

для косинусной составляющей, с аналогичной синусной составляющей в случае комплексного представления. Масштабирующий фактор $K$ является глобальным и инвариантным, так что все базисные значения представляют собой константы времени компиляции, хранимые как неизменяемые целые числа в пространстве имён модуля.

Прямое дискретное целочисленное преобразование (FDIT) над плиткой $\mathbf{b}$ определяется сепарабельно. Сначала выполняется построчное преобразование, дающее промежуточную матрицу $\mathbf{M}$:

$$
M_{u,n} = \sum_{m=0}^{N-1} b_{m,n} \cdot T_{u,m}
$$

затем столбцовое преобразование формирует спектральные коэффициенты:

$$
\hat{b}_{u,v} = \sum_{n=0}^{N-1} M_{u,n} \cdot T_{v,n}
$$

Все суммирования выполняются с использованием 128-битных промежуточных аккумуляторов (эмулируемых посредством явного битового маскирования в Python) для предотвращения переполнения; конечный результат приводится к 64-битному диапазону знаковых целых чисел посредством явного двоично-дополнительного маскирования, устраняя зависимость от неопределённого поведения, обусловленного компилятором или архитектурой процессора.

Фазовая инвариантность обеспечивается вычислением квадрата модуля целочисленных комплексных пар. Если преобразование порождает действительную часть $\Re_{u,v}$ и мнимую часть $\Im_{u,v}$, то фазо-инвариантный коэффициент энергетического спектра равен:

$$
P_{u,v} = \Re_{u,v}^2 + \Im_{u,v}^2
$$

Данная операция отбрасывает угол фазы $\phi_{u,v} = \arctan2(\Im_{u,v}, \Re_{u,v})$ без необходимости вычисления обратной тригонометрической функции с плавающей точкой. Для строго вещественных целочисленных преобразований (например, целочисленных аппроксимаций ДКП) абстракция фазы является неявной величиной модуля коэффициентов. Полученные коэффициенты квантуются в дескриптор с фиксированной точкой посредством равномерного скалярного делителя:

$$
d_{u,v} = \left\lfloor \frac{P_{u,v}}{2^q} \right\rfloor
$$

где $q$ — глобальный параметр фиксированной точки конвейера (по умолчанию $q=10$). Деление реализуется как арифметический сдвиг вправо, гарантирующий единственный однозначный режим округления (округление в направлении минус бесконечности для положительных целых чисел).

**3. Алгоритмическое описание**

Операционный конвейер модуля `sans_phase.py` включает шесть детерминированных этапов:

*Этап 1 — Каноническая загрузка.* Модуль принимает исходные доказательственные буферы от модуля `vigia.io.ingest`, обеспечивающего декодирование носителя в канонический целочисленный растр. При необходимости преобразования цветового пространства (например, в YCbCr или градации серого) модуль использует точные целочисленные матрицы коэффициентов, соответствующие целочисленным аппроксимациям ITU-R BT.601/BT.709, исключая передискретизацию цвета с плавающей точкой.

*Этап 2 — Разбиение на плитки и обработка границ.* Растр разбивается на плитки размером $N \times N$. Крайние плитки, выходящие за пределы изображения, подвергаются детерминированному зеркальному заполнению (вычисление зеркальных индексов посредством целочисленной арифметики) или заполнению нулями в соответствии с политикой конвейера. Логика заполнения не содержит условных ветвлений, зависящих от неинициализированной памяти.

*Этап 3 — Прямое дискретное целочисленное преобразование.* Каждая плитка подвергается сепарабельному FDIT. Реализация выполняет итерации по индексам в фиксированных вложенных циклах, используя исключительно целочисленное сложение, вычитание и умножение. Константы ядра преобразования загружаются из неизменяемого кортежа уровня модуля, гарантируя идентичность базисных значений при каждом выполнении.

*Этап 4 — Обнуление фазы.* Для каждой преобразованной плитки модуль вычисляет $P_{u,v}$ на основе целочисленных комплексных пар или извлекает модуль вещественных коэффициентов. На данном этапе происходит свёртывание фазового измерения, в результате чего формируется представление, инвариантное относительно теоремы сдвига Фурье: пространственные или временные сдвиги входных данных влияют лишь на фазу, оставляя $P_{u,v}$ неизменным.

*Этап 5 — Квантование с фиксированной точкой.* Значения энергетического спектра квантуются указанным арифметическим сдвигом вправо. Выход данного этапа представляет собой массив целых чисел заданной разрядности, пригодный для прямого хеширования или сравнения.

*Этап 6 — Каноническая сериализация.* Результирующие дескрипторы плиток сериализуются в порядке байтов big-endian в соответствии с каноническим байтовым форматом VIGÍA (VCBF). Каждая запись `SansPhaseDescriptor` кодирует координаты плитки $(i,j)$, квантованный спектр $\mathbf{d}$ и опциональную накопительную контрольную сумму при включённом формировании дерева Меркля модулем `vigia.hash.merkle`.

**4. Спецификации входных и выходных данных**

*Входные данные.* Публичный интерфейс `process(evidence_stream: Union[bytes, mmap, VigiaRaster]) -> SansPhaseDescriptorStream` принимает последовательности сырых байтов, отображённые в память судебные образы или предканонизированные растровые объекты. Модуль исходит из предположения, что восходящий уровень загрузки нормализовал разрядность и цветовое пространство; тем не менее, выполняется защитная проверка того, что все входные отсчёты являются целыми числами в ожидаемом домене.

*Выходные данные.* Модуль генерирует детерминированный поток записей `SansPhaseDescriptor`. Внутри реализации вся арифметика использует тип Python `int` произвольной точности, однако на границах операций явно применяется маскирование до 64 или 128 бит для эмуляции поведения АЛУ фиксированной ширины. Данная архитектурная особенность гарантирует идентичность сериализованных байтовых выходных данных независимо от внутреннего представления длинных целых чисел в интерпретаторе Python или разрядности базового процессора.

**5. Детерминистские гарантии и соответствие требованиям цепочки сохранности**

Судебная состоятельность модуля `sans_phase.py` опирается на пять детерминистских гарантий. Первая — **побитово точная воспроизводимость (BER):** при фиксированном входе выходная байтовая последовательность идентична на всех поддерживаемых архитектурах, что подтверждается регрессионным набором модуля `vigia.verify.determinism`. Вторая — **отсутствие загрязнения плавающей точкой:** в модуле отсутствуют вызовы `float`, `math.sin`, `math.cos`, `numpy.float64` и аппаратных FPU-аппроксимаций. Третья — **определённая семантика переполнения:** целочисленное переполнение обрабатывается явным двоично-дополнительным маскированием (`& 0xFFFFFFFFFFFFFFFF`), устраняя дисперсию, обусловленную неопределённым поведением. Четвёртая — **независимость от размещения в памяти:** каноническая сериализация big-endian и явное структурное упаковывание устраняют зависимость от порядка байтов архитектуры. Пятая — **временная стабильность:** выходные данные инвариантны относительно колебаний планирования потоков, пауз сборщика мусора и задержек ввода-вывода, поскольку обработка плиток является безсостоятельной, а порядок потока фиксируется геометрией входных данных.

Указанные свойства сохраняют требования цепочки сохранности, обеспечивая возможность воспроизведения дескрипторов в любой последующий момент с идентичными результатами и позволяя судебному эксперту продемонстрировать отсутствие изменений аналитических артефактов вследствие дрейфа инструментария.

**6. Интеграция со связанными модулями VIGÍA**

Модуль регистрируется в `vigia.sift.core` в качестве обязательной стадии конвейера извлечения признаков. Его выходные данные непосредственно поступают в `vigia.sift.keypoint`, выполняющий обнаружение экстремумов в масштабном пространстве на основе фазо-инвариантных дескрипторов. Проверку целостности осуществляет `vigia.hash.merkle`, запечатывающий каждый блок дескрипторов в криптографическое дерево, устойчивое к подделкам. Метаданные происхождения — включая версию модуля, параметры преобразования $(N, K, q)$ и временную метку выполнения — дополняются модулем `vigia.pipeline.custody` в журнале аудита доказательственных материалов. Непрерывное межплатформенное детерминистское сертифицирование обеспечивается модулем `vigia.verify.determinism`.

**7. Стандартизация и критерии допустимости**

В соответствии со стандартом **Daubert** методология является опровержимой (посредством побитового дифференциального анализа), подвергается рецензированию через документированные открытые константы ядра и демонстрирует известную частоту ошибок, алгоритмически равную нулю при повторном выполнении. Модуль соответствует стандартам **GB/T 29360** (методы судебного исследования электронных данных) и **GB/T 31500** (опорная архитектура больших данных), гарантируя целостность данных, прослеживаемость процесса и воспроизводимость криминалистических производных. Кроме того, он удовлетворяет требованиям схемы **MLPS 2.0** (Multi-Level Protection Scheme 2.0), обеспечивая формирование в защищённых или контролируемых средах неотказуемых, поддающихся аудиту дескрипторов без внедрения побочных каналов, связанных с плавающей точкой, и недетерминистских аппроксимаций.

---

## 中文

**模块名称：** `vigia.sift.sans_phase` — 相位不变确定性预处理子组件

**1. 模块目的与法医理论依据**

`vigia.sift.sans_phase` 模块是VIGÍA数字取证架构中的强制性预处理阶段，具体位于 `vigia.sift` 特征提取子模块内。其核心功能是通过严格离散整数变换，对证据介质进行确定性、逐位可复现的归一化处理，从而抽象出与相位无关的信号特征。在取证实践中，证据 custody chain（保管链）与数字证据的可采性要求分析衍生数据——如特征描述符、哈希输入及相似性度量——在不同计算环境下保持恒定。传统的预处理流水线通常调用浮点快速傅里叶变换（FFT）、三角相位提取以及硬件优化的SIMD近似计算，这些方法会引入平台相关的舍入误差、非确定性分支执行以及库版本差异。`sans_phase.py` 通过将内部运算严格限制在整数算术、预计算超越数常数及显式模约减范围内，彻底消除了上述方差来源，所生成的描述符在x86_64、AArch64与RISC-V平台上逐位一致。该确定性特性直接支撑了Daubert科学证据标准，提供了一种可检验、经同行评审的方法论，其算法错误率已知且受控——对固定输入而言方差为零——并确保下游分析模块接收到的均为标准化、相位无关的特征表示。

**2. 数学基础**

设输入证据信号为离散栅格 $\mathbf{s} \in \mathbb{Z}^{H \times W \times C}$，其中 $H$ 与 $W$ 为空间维度，$C \in \{1,3,4\}$ 为上游摄取层完成规范化后的通道数。每个样本经量化后成为固定比特深度 $B$（通常 $B=16$）的无符号整数。模块将 $\mathbf{s}$ 划分为互不重叠或可选重叠的瓦片（tile） $\mathbf{b}_{i,j} \in \mathbb{Z}^{N \times N}$，以 $(i,j)$ 索引。

核心变换依赖于可分离整数基矩阵 $\mathbf{T} \in \mathbb{Z}^{N \times N}$，该矩阵在运行时无需调用超越函数即可逼近离散傅里叶变换（DFT）或离散余弦变换（DCT）核。$\mathbf{T}$ 的元素以缩放整数形式预计算：

$$
T_{u,m} = \left\lfloor K \cdot \cos\left(\frac{2\pi u m}{N}\right) + \frac{1}{2} \right\rfloor, \quad K = 2^{20}
$$

上式为余弦分量；若变换需要复数表示，则正弦分量按相同方式处理。缩放因子 $K$ 为全局不变量，所有基值均为编译期常数，以不可变整数形式存储于模块命名空间中。

对瓦片 $\mathbf{b}$ 的前向离散整数变换（FDIT）按可分离方式定义。首先进行行变换，得到中间矩阵 $\mathbf{M}$：

$$
M_{u,n} = \sum_{m=0}^{N-1} b_{m,n} \cdot T_{u,m}
$$

随后进行列变换，得到频谱系数：

$$
\hat{b}_{u,v} = \sum_{n=0}^{N-1} M_{u,n} \cdot T_{v,n}
$$

所有求和运算均使用128位中间累加器（在Python中通过显式位掩码模拟）执行，以防止溢出；最终结果通过显式二进制补码掩码归约至64位有符号整数范围，从而消除由编译器或CPU架构导致的未定义行为依赖。

相位不变性通过对整数复数对的模平方计算实现。若变换产生实部 $\Re_{u,v}$ 与虚部 $\Im_{u,v}$，则相位不变功率谱系数为：

$$
P_{u,v} = \Re_{u,v}^2 + \Im_{u,v}^2
$$

该运算丢弃了相位角 $\phi_{u,v} = \arctan2(\Im_{u,v}, \Re_{u,v})$，且无需调用浮点反三角函数。对于严格实整数变换（如整数DCT近似），相位抽象隐含于系数幅值之中。所得系数通过均匀标量除数量化至定点描述符：

$$
d_{u,v} = \left\lfloor \frac{P_{u,v}}{2^q} \right\rfloor
$$

其中 $q$ 为流水线全局定点参数（默认值 $q=10$）。除法以算术右移实现，确保唯一、无歧义的舍入模式（对正整数而言即向负无穷方向舍入）。

**3. 算法描述**

`sans_phase.py` 的运行流水线包含六个确定性阶段：

*阶段1 — 规范摄取。* 模块接收来自 `vigia.io.ingest` 的原始证据缓冲区，该上游组件已将介质解码为规范整数栅格。若需进行色彩空间转换（如转换至YCbCr或灰度），模块采用符合ITU-R BT.601/BT.709整数近似的精确整数系数矩阵，避免浮点色彩重采样。

*阶段2 — 瓦片划分与边界处理。* 栅格被分割为固定尺寸 $N \times N$ 的瓦片。对于超出图像范围的边界瓦片，依据流水线策略执行确定性镜像填充（通过整数运算计算镜像索引）或零填充。填充逻辑不包含依赖于未初始化内存的条件分支。

*阶段3 — 前向离散整数变换。* 每个瓦片依次经过可分离FDIT。实现过程采用固定嵌套循环遍历索引，仅使用整数加法、减法与乘法。变换核常数从模块级不可变元组加载，确保每次执行使用完全相同的基值。

*阶段4 — 相位消除。* 对每个变换后的瓦片，模块由整数复数对计算 $P_{u,v}$，或由实系数提取幅值。该阶段折叠相位维度，生成在傅里叶位移定理下不变的表示：输入在空间或时间上的平移仅影响相位，而 $P_{u,v}$ 保持不变。

*阶段5 — 定点量化。* 功率谱值通过指定的算术右移完成量化。此阶段输出为预定宽度的整数数组，可直接用于哈希运算或比对。

*阶段6 — 规范序列化。* 所得描述符瓦片按VIGÍA规范字节格式（VCBF）以大端序（big-endian）序列化。每个 `SansPhaseDescriptor` 记录编码瓦片坐标 $(i,j)$、量化频谱 $\mathbf{d}$，以及在启用 `vigia.hash.merkle` 集成时可选的累积完整性校验值。

**4. 输入输出规范**

*输入。* 公共接口 `process(evidence_stream: Union[bytes, mmap, VigiaRaster]) -> SansPhaseDescriptorStream` 接受原始字节序列、内存映射的法证镜像或预规范化栅格对象。模块假设上游摄取已完成比特深度与色彩空间的规范化，但会防御性地验证所有输入样本均为预期域内的整数。

*输出。* 模块输出确定性的 `SansPhaseDescriptor` 记录流。内部运算虽使用Python任意精度 `int` 类型，但实现在每次运算边界显式掩码至64位或128位，以模拟定宽ALU行为。该架构决策确保序列化字节输出不受主机Python解释器内部大整数表示或底层处理器字长差异的影响。

**5. 确定性保证与保管链合规性**

`sans_phase.py` 的法医有效性建立在五项确定性保证之上。第一，**逐位精确可复现性（BER）：** 对于固定输入，其输出字节序列在所有受支持架构上完全一致，该属性由 `vigia.verify.determinism` 回归测试套件认证。第二，**无浮点污染：** 模块内部不包含对 `float`、`math.sin`、`math.cos`、`numpy.float64` 或任何硬件FPU近似运算的调用。第三，**定义的溢出语义：** 整数溢出遵循显式二进制补码掩码（`& 0xFFFFFFFFFFFFFFFF`），消除了因未定义行为产生的方差。第四，**内存布局无关性：** 输出采用规范大端序序列化与显式结构打包，消除了因架构字节序差异引入的依赖。第五，**时间稳定性：** 由于瓦片处理为无状态操作且流顺序由输入几何唯一确定，输出不受线程调度波动、垃圾回收停顿及I/O延迟影响。

上述特性保障了保管链要求，确保衍生描述符可在未来任意时刻以完全相同的结果重新生成，使取证人员能够证明分析产物未因工具链漂移而被篡改。

**6. 与相关VIGÍA模块的集成**

该模块在 `vigia.sift.core` 中注册为特征提取流水线的强制性预处理阶段。其输出直接供给 `vigia.sift.keypoint`，用于在相位不变描述符上执行尺度空间极值检测。完整性验证由 `vigia.hash.merkle` 完成，该模块将每个描述符块密封于抗篡改的Merkle密码树中。来源元数据——包括模块版本、变换参数 $(N, K, q)$ 及执行时间戳——由 `vigia.pipeline.custody` 追加至证据审计日志。跨平台确定性认证由 `vigia.verify.determinism` 持续强制执行。

**7. 标准化与可采性标准**

依据 **Daubert** 标准，本方法论具备可检验性（通过逐位差异分析）、经过同行评审（通过公开文档化的核常数）以及已知的错误率（重复执行时算法错误率为零）。该模块符合 **GB/T 29360**（电子数据法医检验方法）与 **GB/T 31500**（大数据参考架构）的要求，保障数据完整性、过程可追溯性及取证衍生结果的可复现性。此外，模块满足 **MLPS 2.0**（网络安全等级保护制度2.0）要求，确保在涉密或受控环境中的取证处理能够生成不可抵赖、可审计的描述符，且不引入浮点侧信道或非确定性近似。