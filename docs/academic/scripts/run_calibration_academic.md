---
doc_hash: 495820ba
module: unknown
languages: [EN, ES, RU]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

## ENGLISH

**Module Designation:** VIGÍA Forensic Calibration Module (`run_calibration.py`, cryptographic hash `495820ba`).  
**Functional Domain:** Empirical calibration of likelihood-ratio (LR) generators within the VIGÍA forensic inference pipeline.

**1. Module Purpose and Forensic Context**
The `run_calibration.py` module constitutes the canonical calibration stage of the VIGÍA ecosystem. Its primary forensic objective is to transform raw, potentially miscalibrated comparison scores—expressed as z-scores extracted from the SYN (synthetic), REAL (authentic), and BEN (benign background) corpora—into probative likelihood ratios (LRs) that satisfy the strictures of evaluative forensic evidence under the Daubert standard (FRE 702/703). In pattern-evidence disciplines such as speaker recognition, handwritten document analysis, and biometric comparison, a raw score produced by a feature extractor does not inherently equate to a statistically interpretable LR. This module closes that epistemic gap by empirically estimating a calibration function $C_{\theta}: \mathbb{R} \to \mathbb{R}^{+}$ that maps standardized z-scores to calibrated LRs, thereby ensuring that the resulting LRs are admissible as quantitative measures of the strength of evidence. By operationalizing Bayes’ theorem in the forensic domain, the module enables the conversion of raw similarity metrics into posterior odds via the relationship $\text{Posterior Odds} = \text{LR} \times \text{Prior Odds}$, with the log-LR $\log_{10}\text{LR}$ corresponding to the weight of evidence in base-10 decibans. A well-calibrated LR guarantees that if a value of $k$ is assigned, the evidence supports the prosecution hypothesis $H_p$ precisely $k$ times more strongly than the defense hypothesis $H_d$.

**2. Mathematical Foundations**
Let $E$ denote the observed evidential feature vector and let $H_p$ and $H_d$ represent the prosecution (same-source) and defense (different-source) hypotheses, respectively. The likelihood ratio is defined as
$$\text{LR} = \frac{p(E \mid H_p)}{p(E \mid H_d)}.$$
In practice, the VIGÍA pipeline first computes a raw similarity score $s$ via the `VIGÍA-Feature-Extractor` and `VIGÍA-Score-Normalizer` modules. The z-score transformation standardizes $s$ relative to a reference population:
$$z = \frac{s - \hat{\mu}_k}{\hat{\sigma}_k}, \quad k \in \{\text{SYN}, \text{REAL}, \text{BEN}\},$$
where $\hat{\mu}_k$ and $\hat{\sigma}_k$ are the sample mean and standard deviation of corpus $k$.

Calibration is framed as the estimation of a parametric or non-parametric transformation that yields $\text{LR}_{\text{cal}} = C_{\theta}(z)$. The VIGÍA LRCalibrator adopts a discriminative approach, minimizing the empirical cross-entropy (Cllr) between the calibrated log-LRs and the ground-truth labels $y_i \in \{0,1\}$. The cost function is
$$\mathcal{L}_{\text{Cllr}}(\theta) = \frac{1}{2N_p}\sum_{i: y_i=1}\log_2\!\bigl(1 + C_{\theta}(z_i)^{-1}\bigr) + \frac{1}{2N_d}\sum_{j: y_j=0}\log_2\!\bigl(1 + C_{\theta}(z_j)\bigr),$$
where $N_p$ and $N_d$ are the counts of same-source and different-source observations. Under the Platt-scaling instantiation implemented in `VIGÍA-LRCalibrator-Core`, the calibration function takes the sigmoidal form
$$P(H_p \mid z) = \frac{1}{1 + \exp(Az + B)}, \quad \text{LR}_{\text{cal}} = \frac{P(H_p \mid z)}{1 - P(H_p \mid z)},$$
with parameters $\theta = \{A, B\} \in \mathbb{R}^2$. Alternative non-parametric formulations—such as isotonic regression, which enforces the monotonicity constraint $\frac{dC}{dz} \ge 0$ to preserve the physical interpretability that higher similarity must map to stronger evidence—or kernel density estimation (KDE), wherein $p(z \mid H_p)$ and $p(z \mid H_d)$ are estimated via non-parametric densities with bandwidth selected by Silverman’s rule or cross-validation, may be selected via configuration. In the KDE case, $\theta$ represents kernel bandwidths or spline knots.

The total empirical cross-entropy decomposes into discrimination loss and calibration loss:
$$\text{Cllr} = \text{Cllr}_{\text{min}} + \text{Cllr}_{\text{cal}}^{\text{loss}},$$
where $\text{Cllr}_{\text{min}}$ reflects the inherent separability of the feature space and $\text{Cllr}_{\text{cal}}^{\text{loss}}$ quantifies the penalty due to miscalibration. The Expected Calibration Error (ECE), computed over $M$ equispaced bins $\{B_m\}_{m=1}^{M}$ on the log-LR axis, is given by
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \Bigl| \text{acc}(B_m) - \text{conf}(B_m) \Bigr|,$$
where $\text{acc}(B_m)$ and $\text{conf}(B_m)$ denote the observed accuracy and predicted confidence within bin $B_m$. Reliability diagrams plot $\text{conf}(B_m)$ against $\text{acc}(B_m)$, and a well-calibrated model exhibits proximity to the diagonal identity line.

**3. Algorithmic Description**
The module executes the following deterministic sequence:

*Step 1 — Environment Sealing.* Upon invocation, the module fixes the global pseudo-random number generator (PRNG) state using a deterministic 32-bit seed derived from the module hash `495820ba`. All non-deterministic execution paths—such as multi-threading reductions, hash-randomization, and BLAS library parallelism—are disabled to guarantee bitwise reproducibility. Environment variables `OPENBLAS_NUM_THREADS=1` and `MKL_NUM_THREADS=1` are enforced.

*Step 2 — Ingestion and Cryptographic Versioning.* The module loads the three corpora via `VIGÍA-Corpus-Manager`. For every file, it computes a SHA-256 digest and validates filenames against an extension whitelist while preventing directory traversal. If the manifest of expected hashes stored in the chain-of-custody ledger mismatches, execution aborts with a `VIGÍAIntegrityError`. This step satisfies GB/T 29360-2012 traceability requirements and Daubert chain-of-custody protocols.

*Step 3 — Z-Score Extraction.* Delegating to `VIGÍA-ZScore-Transformer`, the module computes z-scores for all pairwise or singleton comparisons within each corpus. Out-of-distribution samples exceeding $k=4$ standard deviations are flagged and quarantined in the metadata to prevent corpus shift from biasing $\theta$.

*Step 4 — Dataset Assembly.* A supervised dataset $\mathcal{D} = \{(z_i, y_i)\}_{i=1}^{N}$ is constructed, where $y_i=1$ for same-source pairs and $y_i=0$ for different-source pairs. The module logs class priors and any demographic covariates required by MLPS 2.0 fairness audits.

*Step 5 — Calibration Optimization.* `VIGÍA-LRCalibrator-Core` optimizes $\theta$ via limited-memory BFGS (L-BFGS-B) or Newton-conjugate-gradient, subject to the negative log-likelihood derived from $\mathcal{L}_{\text{Cllr}}$. A multi-start strategy with deterministic seeding mitigates sensitivity to initial values. Convergence tolerances ($\text{gtol} \le 10^{-5}$, $\text{ftol} \le 10^{-7}$) are enforced. For isotonic regression, the Pool-Adjacent-Violators Algorithm (PAVA) is applied under the monotonicity constraint.

*Step 6 — Validation and Metrics Computation.* The module computes $\text{Cllr}$, $\text{ECE}_M$ (with $M=15$ by default), the Area Under the Detection Error Trade-off curve (AUC-DET), and 95% confidence intervals via stratified bootstrap resampling ($B=1000$ replicates, seed-locked). A Daubert-compliance flag is set only if $\text{ECE} < 0.05$ and the confidence interval of $\text{Cllr}$ excludes the uninformative threshold.

*Step 7 — Atomic Persistence.* The fitted parameters $\theta$, calibration family identifier, and corpus provenance hashes are serialized to `models/calibrated_lr.json` using a schema-versioned JSON structure (UTF-8, LF line endings). File writes are atomic (write-to-temp-then-rename) and optionally preceded by JSON Schema validation to prevent corruption during power loss. A reserved digital-signature field is included for future notarization.

*Step 8 — Metadata Commit.* `models/calibration_metadata.json` is updated with: (a) module hash `495820ba`; (b) ISO-8601 timestamp; (c) input SHA-256 catalog; (d) PRNG seed; (e) computed metrics and their confidence intervals; (f) software bill of materials (SBOM) including Python interpreter version and dependency hashes; (g) MLPS 2.0 and Daubert compliance assertions.

*Step 9 — Audit Logging.* An immutable event is appended to `VIGÍA-Audit-Logger`, and the `VIGÍA-Chain-of-Custody` module is notified to advance the forensic provenance graph.

**4. Input/Output Specifications**
*Inputs.*
- `corpora/SYN/`, `corpora/REAL/`, `corpora/BEN/`: directories containing raw or pre-processed forensic samples. Supported formats: WAV, PNG, TXT, or serialized NumPy arrays, as governed by `VIGÍA-Corpus-Manager`.
- `config/calibration_manifest.yaml`: optional configuration specifying calibration family (Platt, isotonic, KDE), regularization penalty $\lambda$, bin count $M$, and OOD threshold $k$.
- `seed`: integer in $[0, 2^{32}-1]$; defaults to the lower 32 bits of `0x495820ba`.

*Outputs.*
- `models/calibrated_lr.json`: schema version `v2.1`; fields `theta` (parameter vector), `calibrator_type` (string), `corpus_hashes` (SHA-256 dict), `fitted_timestamp` (ISO-8601). File mode: 0644, read-only recommended after commit.
- `models/calibration_metadata.json`: schema version `v2.1`; fields `metrics` (nested Cllr, ECE, AUC-DET), `reproducibility` (seed, dependency lock), `compliance_flags` (Daubert, GB/T, MLPS 2.0 booleans), `audit_event_id` (UUIDv4).

**5. Deterministic Guarantees and Standards Compliance**
The module provides deterministic reproducibility: given identical input corpora (verified by SHA-256), identical configuration, and an execution environment matching the SBOM recorded in the metadata, successive invocations produce bitwise-identical `models/calibrated_lr.json` and `models/calibration_metadata.json` files. This guarantee is enforced by (i) a fixed PRNG seed eliminating stochastic gradient perturbations; (ii) disabling Python hash randomization; (iii) sorting all corpus file lists lexicographically before iteration; (iv) single-threaded deterministic reduction for any aggregate operations; and (v) pinning linear-algebra environment variables to prevent BLAS race conditions. Execution inside a containerized environment with a locked image digest (e.g., Docker or Nix) is recommended to further isolate OS-level non-determinism.

Compliance mapping:
- **Daubert / FRE 702–703:** Empirical testing, known error rates (Cllr, ECE), peer-reviewable methodology, and general acceptance are demonstrated via version-controlled, reproducible calibration.
- **GB/T 29360-2012:** Electronic data integrity, traceability, and audit logging are satisfied by cryptographic hashing and immutable metadata.
- **MLPS 2.0:** Data-handling security, non-repudiation, and provenance tracking are enforced through `VIGÍA-Chain-of-Custody` and audit logging.

**6. Integration with Related VIGÍA Modules**
- `VIGÍA-LRCalibrator-Core`: provides the optimization engine and parameterization family.
- `VIGÍA-Corpus-Manager`: handles ingestion, format normalization, and hash verification.
- `VIGÍA-Feature-Extractor` / `VIGÍA-Score-Normalizer`: upstream modules producing raw scores that are transformed into z-scores.
- `VIGÍA-ZScore-Transformer`: computes standardized scores and OOD flags.
- `VIGÍA-Validation-Engine`: downstream module that consumes `calibrated_lr.json` to evaluate case-work LRs.
- `VIGÍA-Audit-Logger` / `VIGÍA-Chain-of-Custody`: ensure forensic provenance and tamper evidence.
- `VIGÍA-Report-Generator`: ingests metadata to produce court-admissible calibration reports.

**7. Conclusion**
The VIGÍA calibration module (`495820ba`) operationalizes the transition from heuristic similarity scores to legally defensible likelihood ratios. By embedding deterministic reproducibility, cryptographic versioning, and rigorous cross-entropy minimization within a standardized pipeline, the module satisfies the highest echelons of forensic scientific rigor required under Daubert, GB/T, and MLPS 2.0 frameworks.

## ESPAÑOL

**Designación del módulo:** Módulo de Calibración Forense VIGÍA (`run_calibration.py`, hash criptográfico `495820ba`).  
**Dominio funcional:** Calibración empírica de generadores de razón de verosimilitud (likelihood ratio, LR) dentro del pipeline de inferencia forense VIGÍA.

**1. Propósito del módulo y contexto forense**
El presente módulo constituye la etapa canónica de calibración del ecosistema VIGÍA. Su objetivo forense primordial consiste en transformar puntuaciones de comparación cruda, expresadas como z-scores extraídos de los corpus SYN (sintético), REAL (auténtico) y BEN (benigno o de fondo), en razones de verosimilitud probativas que satisfagan los requisitos del estándar Daubert (FRE 702/703). En disciplinas de evidencia de patrones —tales como reconocimiento de habla, análisis de escritura manuscrita o comparación biométrica—, una puntuación cruda producida por un extractor de rasgos no equivale per se a una LR estadísticamente interpretable. Este módulo colma esa brecha epistémica estimando empíricamente una función de calibración $C_{\theta}: \mathbb{R} \to \mathbb{R}^{+}$ que mapea z-scores estandarizados hacia LRs calibradas, garantizando que las LRs resultantes sean admisibles como medidas cuantitativas de la fuerza de la evidencia. Al operacionalizar el teorema de Bayes en el dominio forense, el módulo permite convertir métricas heurísticas de similitud en odds a posteriori mediante la relación $\text{Odds Posterior} = \text{LR} \times \text{Odds Prior}$, siendo $\log_{10}\text{LR}$ el peso de la evidencia en decibanios base-10. Una LR bien calibrada asegura que, si se asigna un valor $k$, la evidencia respalda la hipótesis de acusación $H_p$ exactamente $k$ veces más fuertemente que la hipótesis de defensa $H_d$.

**2. Fundamentos matemáticos**
Sea $E$ el vector de rasgos evidenciales observado, y sean $H_p$ y $H_d$ las hipótesis de acusación (misma fuente) y defensa (fuente distinta), respectivamente. La razón de verosimilitud se define como
$$\text{LR} = \frac{p(E \mid H_p)}{p(E \mid H_d)}.$$
En la práctica, el pipeline VIGÍA computa primero una puntuación de similitud cruda $s$ mediante los módulos `VIGÍA-Feature-Extractor` y `VIGÍA-Score-Normalizer`. La transformación a z-score estandariza $s$ respecto de una población de referencia:
$$z = \frac{s - \hat{\mu}_k}{\hat{\sigma}_k}, \quad k \in \{\text{SYN}, \text{REAL}, \text{BEN}\},$$
donde $\hat{\mu}_k$ y $\hat{\sigma}_k$ son la media muestral y el desvío estándar del corpus $k$.

La calibración se enmarca como la estimación de una transformación paramétrica o no paramétrica que produce $\text{LR}_{\text{cal}} = C_{\theta}(z)$. El LRCalibrator de VIGÍA adopta un enfoque discriminativo, minimizando la entropía cruzada empírica (Cllr) entre los log-LR calibrados y las etiquetas de verdad fundacional $y_i \in \{0,1\}$. La función de costo es
$$\mathcal{L}_{\text{Cllr}}(\theta) = \frac{1}{2N_p}\sum_{i: y_i=1}\log_2\!\bigl(1 + C_{\theta}(z_i)^{-1}\bigr) + \frac{1}{2N_d}\sum_{j: y_j=0}\log_2\!\bigl(1 + C_{\theta}(z_j)\bigr),$$
donde $N_p$ y $N_d$ son los recuentos de observaciones de misma fuente y fuente distinta. Bajo la instanciación de escala de Platt implementada en `VIGÍA-LRCalibrator-Core`, la función de calibración adopta la forma sigmoidea
$$P(H_p \mid z) = \frac{1}{1 + \exp(Az + B)}, \quad \text{LR}_{\text{cal}} = \frac{P(H_p \mid z)}{1 - P(H_p \mid z)},$$
con parámetros $\theta = \{A, B\} \in \mathbb{R}^2$. Formulaciones no paramétricas alternativas —como la regresión isotónica, que impone la restricción de monotonicidad $\frac{dC}{dz} \ge 0$ para preservar la interpretabilidad física de que mayor similitud debe mapear a evidencia más fuerte, o la estimación de densidad por núcleos (KDE), en la cual $p(z \mid H_p)$ y $p(z \mid H_d)$ se aproximan mediante densidades no paramétricas con ancho de banda seleccionado por la regla de Silverman o validación cruzada— podrían seleccionarse vía configuración. En el caso KDE, $\theta$ representa los anchos de banda del núcleo o los nudos de spline.

La entropía cruzada empírica total se descompone en pérdida de discriminación y pérdida de calibración:
$$\text{Cllr} = \text{Cllr}_{\text{min}} + \text{Cllr}_{\text{cal}}^{\text{pérdida}},$$
donde $\text{Cllr}_{\text{min}}$ refleja la separabilidad inherente del espacio de rasgos y $\text{Cllr}_{\text{cal}}^{\text{pérdida}}$ cuantifica la penalización debida a descalibración. El Error de Calibración Esperado (ECE), computado sobre $M$ intervalos equiespaciados $\{B_m\}_{m=1}^{M}$ en el eje log-LR, viene dado por
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \Bigl| \text{acc}(B_m) - \text{conf}(B_m) \Bigr|,$$
donde $\text{acc}(B_m)$ y $\text{conf}(B_m)$ denotan la exactitud observada y la confianza predicha dentro del intervalo $B_m$. Los diagramas de confiabilidad grafican $\text{conf}(B_m)$ frente a $\text{acc}(B_m)$, y un modelo bien calibrado exhibe proximidad a la diagonal identidad.

**3. Descripción algorítmica**
El módulo ejecuta la siguiente secuencia determinística:

*Paso 1 — Sellado del ambiente.* Al invocarse, el módulo fija el estado global del generador de números pseudoaleatorios (PRNG) mediante una semilla de 32 bits derivada del hash `495820ba`. Todas las rutinas de ejecución no determinísticas —tales como reducciones multihilo, aleatorización de hashes y paralelismo de bibliotecas BLAS— se desactivan para garantizar reproducibilidad bit a bit. Se imponen las variables de entorno `OPENBLAS_NUM_THREADS=1` y `MKL_NUM_THREADS=1`.

*Paso 2 — Ingesta y versionado criptográfico.* El módulo carga los tres corpus mediante `VIGÍA-Corpus-Manager`. Para cada archivo, computa un digest SHA-256 y valida las extensiones contra una lista blanca, previniendo recorridas de directorio. Si el manifiesto de hashes esperados, almacenado en el registro de cadena de custodia, no coincide, la ejecución se interrumpe con un `VIGÍAIntegrityError`. Este paso satisface los requisitos de trazabilidad de la norma GB/T 29360-2012 y los protocolos de cadena de custodia de Daubert.

*Paso 3 — Extracción de z-scores.* Delegando en `VIGÍA-ZScore-Transformer`, el módulo computa los z-scores para todas las comparaciones por pares o singleton dentro de cada corpus. Las muestras fuera de distribución que exceden $k=4$ desvíos estándar se marcan y se ponen en cuarentena en los metadatos para evitar que el desplazamiento de corpus sesgue $\theta$.

*Paso 4 — Ensamblado del conjunto de datos.* Se construye un conjunto supervisado $\mathcal{D} = \{(z_i, y_i)\}_{i=1}^{N}$, donde $y_i=1$ para pares de misma fuente e $y_i=0$ para pares de fuente distinta. El módulo registra los priors de clase y cualquier covariable demográfica exigida por las auditorías de equidad de MLPS 2.0.

*Paso 5 — Optimización de calibración.* `VIGÍA-LRCalibrator-Core` optimiza $\theta$ vía L-BFGS-B o gradiente conjugado de Newton, sujeto a la log-verosimilitud negativa derivada de $\mathcal{L}_{\text{Cllr}}$. Una estrategia de múltiples arranques (multi-start) con semilla determinística mitiga la sensibilidad a los valores iniciales. Se imponen tolerancias de convergencia ($\text{gtol} \le 10^{-5}$, $\text{ftol} \le 10^{-7}$). Para regresión isotónica, se aplica el Algoritmo de Violadores Adyacentes de Piscinas (PAVA) bajo la restricción de monotonicidad.

*Paso 6 — Validación y computación de métricas.* El módulo computa $\text{Cllr}$, $\text{ECE}_M$ (con $M=15$ por defecto), el área bajo la curva de error de detección (AUC-DET) e intervalos de confianza del 95 % mediante remuestreo bootstrap estratificado ($B=1000$ replicados, semilla fija). Se activa la bandera de cumplimiento Daubert solo si $\text{ECE} < 0,05$ y el intervalo de confianza de $\text{Cllr}$ excluye el umbral no informativo.

*Paso 7 — Persistencia atómica.* Los parámetros ajustados $\theta$, el identificador de familia de calibración y los hashes de procedencia de los corpus se serializan en `models/calibrated_lr.json` mediante una estructura JSON con versión de esquema (UTF-8, finales de línea LF). Las escrituras de archivo son atómicas (escritura temporal y renombre) y opcionalmente precedidas por validación contra JSON Schema para prevenir corrupción ante fallos de energía. Se incluye un campo reservado para firma digital destinado a futura notarización.

*Paso 8 — Registro de metadatos.* Se actualiza `models/calibration_metadata.json` con: (a) hash del módulo `495820ba`; (b) marca temporal ISO-8601; (c) catálogo SHA-256 de entradas; (d) semilla del PRNG; (e) métricas computadas y sus intervalos de confianza; (f) lista de materiales de software (SBOM) incluyendo la versión del intérprete Python y los hashes de dependencias; (g) aserciones de cumplimiento MLPS 2.0 y Daubert.

*Paso 9 — Registro de auditoría.* Se agrega un evento inmutable a `VIGÍA-Audit-Logger` y se notifica a `VIGÍA-Chain-of-Custody` para avanzar el grafo de procedencia forense.

**4. Especificaciones de entrada y salida**
*Entradas.*  
Vos debés suministrar los directorios `corpora/SYN/`, `corpora/REAL/` y `corpora/BEN/`, que contienen las muestras forenses brutas o preprocesadas. Los formatos soportados (WAV, PNG, TXT, matrices serializadas de NumPy) están regulados por `VIGÍA-Corpus-Manager`.  
Opcionalmente, podés incluir el archivo `config/calibration_manifest.yaml`, donde especifiqués la familia de calibración (Platt, isotónica, KDE), el coeficiente de regularización $\lambda$, la cantidad de intervalos $M$ y el umbral de exclusión $k$ para muestras fuera de distribución.  
La semilla `seed` es un entero comprendido en $[0, 2^{32}-1]$; si no la indicás, el sistema emplea los 32 bits menos significativos de `0x495820ba`.

*Salidas.*  
El módulo te generará el archivo `models/calibrated_lr.json`, cuyo esquema es `v2.1`; los campos incluyen `theta` (vector de parámetros), `calibrator_type` (cadena), `corpus_hashes` (diccionario de SHA-256) y `fitted_timestamp` (ISO-8601). El modo de archivo es 0644; te sugerimos fuertemente que lo dejés como solo lectura una vez efectuado el commit.  
Además, recibirás `models/calibration_metadata.json` (esquema `v2.1`), con campos anidados para métricas (`metrics`), artefactos de reproducibilidad (`reproducibility`), indicadores de cumplimiento (`compliance_flags`) y un identificador de evento de auditoría (`audit_event_id`, UUIDv4).

**5. Garantías determinísticas y cumplimiento normativo**
El módulo te brinda garantías deterministas de reproducibilidad: si proporcionás corpus de entrada idénticos —verificá siempre sus SHA-256—, una configuración idéntica y un entorno de ejecución que se corresponda con el SBOM registrado en los metadatos, las sucesivas invocaciones te producirán archivos `models/calibrated_lr.json` y `models/calibration_metadata.json` idénticos bit a bit. Esta propiedad se asegura mediante (i) una semilla fija de PRNG que anula fluctuaciones estocásticas en el gradiente; (ii) la desactivación de la aleatorización de hashes de Python; (iii) el ordenamiento lexicográfico previo de toda lista de archivos de corpus antes de la iteración; (iv) reducciones agregadas de un solo hilo para eliminar condiciones de carrera; y (v) el fijado de las variables de entorno `OPENBLAS_NUM_THREADS=1` y `MKL_NUM_THREADS=1`, de modo de neutralizar indeterminismos en bibliotecas de álgebra lineal subyacente. Se recomienda ejecutar el módulo dentro de un entorno contenedorizado con digest de imagen bloqueado (p. ej., Docker o Nix) para aislar aún más las fuentes de no determinismo a nivel de sistema operativo.

El cumplimiento normativo se vincula de la siguiente manera:
- **Daubert / FRE 702–703:** La prueba empírica, las tasas de error conocidas (Cllr, ECE), la metodología susceptible de revisión por pares y la aceptación general se demuestran mediante una calibración versionada y reproducible.
- **GB/T 29360-2012:** La integridad de los datos electrónicos, la trazabilidad y el registro de auditoría se satisfacen mediante el hash criptográfico y los metadatos inmutables.
- **MLPS 2.0:** La seguridad en el manejo de datos, la no repudiación y el rastreo de procedencia se aplican a través de `VIGÍA-Chain-of-Custody` y el registro de auditoría.

**6. Integración con módulos VIGÍA relacionados**
- `VIGÍA-LRCalibrator-Core`: provee el motor de optimización y la familia de parametrización.
- `VIGÍA-Corpus-Manager`: gestiona la ingestión, la normalización de formatos y la verificación de hashes.
- `VIGÍA-Feature-Extractor` / `VIGÍA-Score-Normalizer`: módulos aguas arriba que producen las puntuaciones crudas transformadas luego en z-scores.
- `VIGÍA-ZScore-Transformer`: computa las puntuaciones estandarizadas y las banderas de OOD.
- `VIGÍA-Validation-Engine`: módulo aguas abajo que consume `calibrated_lr.json` para evaluar LRs en casos reales.
- `VIGÍA-Audit-Logger` / `VIGÍA-Chain-of-Custody`: garantizan la procedencia forense y la evidencia de manipulación.
- `VIGÍA-Report-Generator`: ingiere los metadatos para producir informes de calibración admisibles en sede judicial.

**7. Conclusión**
El módulo de calibración VIGÍA (`495820ba`) operativiza la transición desde puntuaciones heurísticas de similitud hacia razones de verosimilitud jurídicamente defendibles. Al incorporar reproducibilidad determinística, versionado criptográfico y minimización rigurosa de la entropía cruzada dentro de un pipeline estandarizado, el módulo satisface los más altos estándares de rigor científico forense exigidos por los marcos Daubert, GB/T y MLPS 2.0.

## РУССКИЙ

**Обозначение модуля:** Модуль судебной калибровки VIGÍA (`run_calibration.py`, криптографический хэш `495820ba`).  
**Функциональная область:** Эмпирическая калибровка генераторов отношения правдоподобия (LR) в рамках судебного пайплайна инференса VIGÍA.

**1. Назначение модуля и судебный контекст**
Модуль `run_calibration.py` представляет собой каноническую стадию калибровки экосистемы VIGÍA. Его основная судебная задача заключается в преобразовании необработанных, потенциально некалиброванных сравнительных оценок, выраженных в виде z-оценок, извлечённых из корпусов SYN (синтетический), REAL (аутентичный) и BEN (фоновый), в пробативные отношения правдоподобия (LR), удовлетворяющие требованиям стандарта Daubert (FRE 702/703). В дисциплинах, оперирующих доказательствами на основе паттернов (распознавание диктора, почерковедческая экспертиза, биометрическое сравнение), необработанная оценка, выданная извлекателем признаков, сама по себе не эквивалентна статистически интерпретируемому LR. Настоящий модуль устраняет этот эпистемологический разрыв путём эмпирического оценивания калибровочной функции $C_{\theta}: \mathbb{R} \to \mathbb{R}^{+}$, отображающей стандартизированные z-оценки в калиброванные LR, что гарантирует допустимость полученных LR в качестве количественных мер силы доказательства. Операционализируя теорему Байеса в судебной области, модуль позволяет преобразовывать эвристические метрики сходства в апостериорные шансы посредством соотношения $\text{Posterior Odds} = \text{LR} \times \text{Prior Odds}$, при этом $\log_{10}\text{LR}$ соответствует весу доказательства в децибанах по основанию 10. Хорошо откалиброванное LR гарантирует, что если присвоено значение $k$, то доказательства поддерживают обвинительную гипотезу $H_p$ ровно в $k$ раз сильнее, чем гипотезу защиты $H_d$.

**2. Математические основания**
Пусть $E$ обозначает наблюдаемый вектор признаков доказательства, а $H_p$ и $H_d$ — гипотезы обвинения (общий источник) и защиты (различные источники) соответственно. Отношение правдоподобия определяется как
$$\text{LR} = \frac{p(E \mid H_p)}{p(E \mid H_d)}.$$
На практике пайплайн VIGÍA сначала вычисляет необработанную оценку сходства $s$ посредством модулей `VIGÍA-Feature-Extractor` и `VIGÍA-Score-Normalizer`. Преобразование в z-оценку стандартизирует $s$ относительно референтной совокупности:
$$z = \frac{s - \hat{\mu}_k}{\hat{\sigma}_k}, \quad k \in \{\text{SYN}, \text{REAL}, \text{BEN}\},$$
где $\hat{\mu}_k$ и $\hat{\sigma}_k$ — выборочное среднее и стандартное отклонение корпуса $k$.

Калибровка формулируется как оценка параметрического или непараметрического преобразования, порождающего $\text{LR}_{\text{cal}} = C_{\theta}(z)$. Калибратор VIGÍA LRCalibrator применяет дискриминативный подход, минимизируя эмпирическую перекрёстную энтропию (Cllr) между калиброванными логарифмами LR и метками истинности $y_i \in \{0,1\}$. Целевая функция имеет вид
$$\mathcal{L}_{\text{Cllr}}(\theta) = \frac{1}{2N_p}\sum_{i: y_i=1}\log_2\!\bigl(1 + C_{\theta}(z_i)^{-1}\bigr) + \frac{1}{2N_d}\sum_{j: y_j=0}\log_2\!\bigl(1 + C_{\theta}(z_j)\bigr),$$
где $N_p$ и $N_d$ — число наблюдений общего и различного источника. В рамках реализации масштабирования Платта (Platt scaling), осуществляемой в `VIGÍA-LRCalibrator-Core`, калибровочная функция принимает сигмоидальный вид
$$P(H_p \mid z) = \frac{1}{1 + \exp(Az + B)}, \quad \text{LR}_{\text{cal}} = \frac{P(H_p \mid z)}{1 - P(H_p \mid z)},$$
с параметрами $\theta = \{A, B\} \in \mathbb{R}^2$. Альтернативные непараметрические формулировки — например, изотоническая регрессия, накладывающая ограничение монотонности $\frac{dC}{dz} \ge 0$ для сохранения физической интерпретируемости, при которой большая сходство должна соответствовать более сильным доказательствам, или оценка плотности ядра (KDE), при которой $p(z \mid H_p)$ и $p(z \mid H_d)$ аппроксимируются непараметрическими плотностями с шириной полосы, выбираемой по правилу Сильвермана или скользящего контроля — могут быть выбраны через конфигурацию. При использовании KDE $\theta$ представляет ширину полосы пропускания ядра или узлы сплайна.

Полная эмпирическая перекрёстная энтропия раскладывается на дискриминационную потерю и калибровочную потерю:
$$\text{Cllr} = \text{Cllr}_{\text{min}} + \text{Cllr}_{\text{cal}}^{\text{loss}},$$
где $\text{Cllr}_{\text{min}}$ отражает присущую разделимость пространства признаков, а $\text{Cllr}_{\text{cal}}^{\text{loss}}$ количественно оценивает штраф за некалиброванность. Ожидаемая ошибка калибровки (ECE), вычисляемая по $M$ равноотстоящим интервалам $\{B_m\}_{m=1}^{M}$ на оси логарифма LR, задаётся выражением
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \Bigl| \text{acc}(B_m) - \text{conf}(B_m) \Bigr|,$$
где $\text{acc}(B_m)$ и $\text{conf}(B_m)$ — наблюдаемая точность и предсказанная уверенность внутри интервала $B_m$. Диаграммы надёжности отображают $\text{conf}(B_m)$ относительно $\text{acc}(B_m)$, и хорошо откалиброванная модель демонстрирует близость к диагональной линии тождества.

**3. Алгоритмическое описание**
Модуль выполняет следующую детерминированную последовательность:

*Шаг 1 — Фиксация среды выполнения.* При вызове модуль фиксирует глобальное состояние генератора псевдослучайных чисел (PRNG) с помощью детерминированного 32-разрядного начального значения, производного от хэша `495820ba`. Все недетерминированные пути выполнения — такие как многопоточные редукции, рандомизация хэшей и параллелизм библиотек BLAS — отключаются для гарантии побитовой воспроизводимости. Устанавливаются переменные среды `OPENBLAS_NUM_THREADS=1` и `MKL_NUM_THREADS=1`.

*Шаг 2 — Инжестия и криптографическое версионирование.* Модуль загружает три корпуса через `VIGÍA-Corpus-Manager`. Для каждого файла вычисляется дайджест SHA-256 и производится валидация расширений файлов по белому списку с предотвращением обхода каталогов. При несоответствии манифеста ожидаемых хэшей (хранимого в реестре цепочки сохранения) выполнение прерывается с исключением `VIGÍAIntegrityError`. Данный шаг удовлетворяет требованиям прослеживаемости стандарта GB/T 29360-2012 и протоколам цепочки сохранения Daubert.

*Шаг 3 — Извлечение z-оценок.* Делегируя операции модулю `VIGÍA-ZScore-Transformer`, модуль вычисляет z-оценки для всех попарных или одиночных сравнений внутри каждого корпуса. Образцы, выходящие за пределы распределения и превышающие $k=4$ стандартных отклонений, помечаются и помещаются в карантин в метаданных, чтобы смещение корпуса не исказило $\theta$.

*Шаг 4 — Формирование обучающего множества.* Конструируется контролируемый набор данных $\mathcal{D} = \{(z_i, y_i)\}_{i=1}^{N}$, где $y_i=1$ для пар общего источника и $y_i=0$ для пар различного источника. Модуль регистрирует априорные вероятности классов и демографические ковариаты, требуемые аудитом справедливости MLPS 2.0.

*Шаг 5 — Оптимизация калибровки.* `VIGÍA-LRCalibrator-Core` оптимизирует $\theta$ методом L-BFGS-B или сопряжённых градиентов Ньютона, минимизируя отрицательную логарифмическую правдоподобие, производную от $\mathcal{L}_{\text{Cllr}}$. Стратегия множественного запуска (multi-start) с детерминированной фиксацией начального значения снижает чувствительность к стартовым точкам. Устанавливаются допуски сходимости ($\text{gtol} \le 10^{-5}$, $\text{ftol} \le 10^{-7}$). Для изотонической регрессии применяется алгоритм PAVA при ограничении монотонности.

*Шаг 6 — Валидация и расчёт метрик.* Модуль вычисляет $\text{Cllr}$, $\text{ECE}_M$ (по умолчанию $M=15$), площадь под кривой ошибок обнаружения (AUC-DET) и 95%-ные доверительные интервалы посредством стратифицированного бутстрепа ($B=1000$ реплик, с фиксацией начального значения). Флаг соответствия Daubert устанавливается только при $\text{ECE} < 0{,}05$ и условии, что доверительный интервал $\text{Cllr}$ не включает неинформативный порог.

*Шаг 7 — Атомарное сохранение.* Подогнанные параметры $\theta$, идентификатор семейства калибровки и хэши происхождения корпусов сериализуются в `models/calibrated_lr.json` в виде структуры JSON с версией схемы (UTF-8, окончания строк LF). Запись файлов осуществляется атомарно (запись во временный файл с последующим переименованием) и опционально предваряется валидацией по JSON Schema для предотвращения повреждения при сбое питания. Включено зарезервированное поле для цифровой подписи, предназначенное для будущей нотариализации.

*Шаг 8 — Фиксация метаданных.* Файл `models/calibration_metadata.json` обновляется следующими данными: (a) хэш модуля `495820ba`; (b) метка времени ISO-8601; (c) каталог SHA-256 входных данных; (d) начальное значение PRNG; (e) рассчитанные метрики и их доверительные интервалы; (f) программный перечень материалов (SBOM), включая версию интерпретатора Python и хэши зависимостей; (g) утверждения о соответствии стандартам MLPS 2.0 и Daubert.

*Шаг 9 — Аудит.* Неизменяемое событие добавляется в `VIGÍA-Audit-Logger`, а модуль `VIGÍA-Chain-of-Custody` получает уведомление для продвижения графа судебного происхождения.

**4. Спецификации входных и выходных данных**
*Входные данные.*  
- `corpora/SYN/`, `corpora/REAL/`, `corpora/BEN/`: каталоги с необработанными или предобработанными судебными образцами. Поддерживаемые форматы (WAV, PNG, TXT, сериализованные массивы NumPy) определяются модулем `VIGÍA-Corpus-Manager`.  
- `config/calibration_manifest.yaml`: необязательная конфигурация, задающая семейство калибровки (Platt, изотоническая, KDE), штраф регуляризации $\lambda$, число интервалов $M$ и порог OOD $k$.  
- `seed`: целое число из диапазона $[0, 2^{32}-1]$; по умолчанию используются младшие 32 бита `0x495820ba`.

*Выходные данные.*  
- `models/calibrated_lr.json`: версия схемы `v2.1`; поля `theta` (вектор параметров), `calibrator_type` (строка), `corpus_hashes` (словарь SHA-256), `fitted_timestamp` (ISO-8601). Права доступа: 0644, после фиксации рекомендуется режим «только чтение».  
- `models/calibration_metadata.json`: версия схемы `v2.1`; поля `metrics` (вложенные Cllr, ECE, AUC-DET), `reproducibility` (начальное значение, блокировка зависимостей), `compliance_flags` (логические признаки Daubert, GB/T, MLPS 2.0), `audit_event_id` (UUIDv4).

**5. Детерминированные гарантии и нормативное соответствие**
Модуль обеспечивает детерминированную воспроизводимость: при идентичных входных корпусах (верифицируемых по SHA-256), идентичной конфигурации и среде выполнения, соответствующей SBOM, зафиксированному в метаданных, повторные вызовы порождают побитово идентичные файлы `models/calibrated_lr.json` и `models/calibration_metadata.json`. Эта гарантия реализуется за счёт (i) фиксации начального значения PRNG, исключающей стохастические флуктуации градиента; (ii) отключения рандомизации хэшей в Python; (iii) лексикографической сортировки всех списков файлов корпуса перед итерацией; (iv) однопоточных детерминированных редукций для всех агрегирующих операций; и (v) фиксации переменных среды `OPENBLAS_NUM_THREADS=1` и `MKL_NUM_THREADS=1` для устранения неопределённости в базовых библиотеках линейной алгебры. Рекомендуется выполнение модуля внутри контейнеризированной среды с зафиксированным дайджестом образа (например, Docker или Nix) для дополнительной изоляции от недетерминизма на уровне операционной системы.

Карта нормативного соответствия:
- **Daubert / FRE 702–703:** Эмпирическое тестирование, известные частоты ошибок (Cllr, ECE), методология, доступная для рецензирования, и общее признание демонстрируются посредством версионированной и воспроизводимой калибровки.
- **GB/T 29360-2012:** Целостность электронных данных, прослеживаемость и аудит обеспечиваются криптографическим хэшированием и неизменяемыми метаданными.
- **MLPS 2.0:** Безопасность обращения с данными, невозможность отказа от авторства и отслеживание происхождения обеспечиваются модулями `VIGÍA-Chain-of-Custody` и аудит-логированием.

**6. Интеграция со смежными модулями VIGÍA**
- `VIGÍA-LRCalibrator-Core`: предоставляет оптимизационный движок и семейство параметризаций.
- `VIGÍA-Corpus-Manager`: осуществляет инжестию, нормализацию форматов и верификацию хэшей.
- `VIGÍA-Feature-Extractor` / `VIGÍA-Score-Normalizer`: выш