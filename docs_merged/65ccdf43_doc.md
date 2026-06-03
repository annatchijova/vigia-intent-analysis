<!--
VIGIA Academic Documentation
Module: 65ccdf43
Batch ID: vigia-doc-0053-65ccdf43
Generated: 2026-05-20T14:56:47.855837+00:00
-->

### ENGLISH

#### What Is This Module?
This script, `fit_calibration.py`, is the empirical calibration engine of the VIGIA Forensic Suite. Its purpose is to train statistical reference models that quantify how much a digital artifact deviates from authentic content. Think of it as a metrological instrument: before a sensor can measure pressure or temperature, it must be calibrated against known reference samples. Here, the "sensor" is the forensic tool's z-score output, and the reference samples are documents known to be authentic (H0) or fabricated/adversarial (H1). The module produces three artifacts: (1) calibrated KDE models per tool, (2) regularized covariance matrices for the NLP tool cluster, and (3) a metadata JSON file ensuring complete traceability (Daubert compliance). It uses deterministic integer arithmetic for indexing, counting, and partitioning, and exact cryptographic hashing (SHA-256) for dataset identification.

#### Key Concepts

| Concept | Description | Role in Calibration |
|---|---|---|
| **Kernel Density Estimation (KDE)** | A non-parametric model that reconstructs a probability distribution from exact counts of reference observations. | Builds the H0 and H1 likelihood models for each forensic tool. |
| **Bandwidth** | The smoothing scope determined by a deterministic scan over a pre-defined, integer-indexed grid. | Controls model resolution; selected via exhaustive grid search, not guessed. |
| **GridSearchCV** | An exhaustive, deterministic algorithm that evaluates every candidate on an integer-indexed grid using exact fold counts. | Guarantees reproducible bandwidth selection. |
| **H0 / H1 Hypotheses** | H0: Authentic content. H1: Fabricated or adversarially modified content. | The two reference populations against which evidence is weighed. |
| **Ledoit-Wolf Shrinkage** | A deterministic regularization method that computes well-conditioned covariance matrices from exact integer sample counts. | Prevents numerical degeneracy in the NLP cluster when pooling multiple tools. |
| **SHA-256 Canonical Hash** | A 256-bit deterministic integer fingerprint of the entire calibration dataset. | Provides Daubert-grade traceability and tamper detection. |
| **Z-Score** | A standardized deviation measurement produced by a forensic tool. | The raw integer-scaled signal fed into the calibration models. |
| **Covariance / Precision** | Matrices describing joint variability among tools and its exact algebraic inverse. | Enables multivariate scoring for the NLP cluster (SDA, ACP, CLI, ROI). |
| **Traceability Metadata** | A JSON file recording dataset hash, selected bandwidths, exact sample sizes, and shrinkage values. | The calibration certificate required for courtroom admissibility. |

#### Glossary of Technical Terms

- **Calibration**: The process of mapping raw instrument readings (z-scores) onto a validated probability scale using known reference samples.
- **Cross-Validation (CV)**: Partitioning the dataset into an exact integer number of folds (`CV_FOLDS`) to test model stability without wasting data.
- **Daubert Standard**: A legal criterion requiring scientific methods to be testable, peer-reviewed, and accompanied by known error rates and traceability.
- **Deterministic Integer Arithmetic**: Calculations performed on exact counts and indices, ensuring that every run with the same data produces identical results.
- **Forensic Artifact**: Any digital object submitted for examination; in this context, also refers to the output files (models and metadata).
- **Likelihood Ratio (LR)**: The relative weight of evidence, computed as the ratio of probabilities under H1 versus H0.
- **NLP Cluster**: The set of Natural Language Processing tools (SDA, ACP, CLI, ROI) whose outputs are correlated and therefore modeled jointly.
- **Non-Parametric Model**: A statistical model that does not assume a fixed mathematical shape (e.g., normal curve), but instead follows the exact data distribution.
- **Regularization**: A deterministic procedure that mathematically stabilizes a model when sample counts are finite.
- **Synthetic Dataset**: An artificially generated reference set with controlled, known properties used to validate the calibration pipeline.

#### 【Scientific Note】
Within the broader VIGIA framework, you may encounter terminology drawn from **Peircean semiotics**, **Eco's** (Umberto Eco) theory of codes, and **Grice's** maxims of communication. These terms are **not mysticism**. They function exactly like the calibration protocol of a laboratory sensor. A thermocouple does not "magically" know temperature; it produces a voltage that acquires meaning only after being mapped to a reference scale through a deterministic calibration curve. Likewise, Peirce's signs, Eco's cultural codes, and Grice's conversational implicatures are formal conventions for mapping signals to states of the world. In `fit_calibration.py`, the z-scores are meaningless voltages until this module maps them to exact H0 and H1 reference distributions. The semiotic vocabulary is therefore metrological: it describes how a forensic signal acquires evidential meaning through calibrated reference to known standards.

---

**ESPAÑOL Section**:

### ESPAÑOL

#### ¿Qué es este módulo?
Este script, `fit_calibration.py`, es el motor de calibración empírica del VIGIA Forensic Suite. Su propósito es entrenar modelos de referencia estadística que cuantifiquen cuánto se desvía un artefacto digital del contenido auténtico. Piense en él como un instrumento metrológico: antes de que un sensor pueda medir presión o temperatura, debe calibrarse contra muestras de referencia conocidas. Aquí, el "sensor" es la salida de z-scores de la herramienta forense, y las muestras de referencia son documentos conocidos como auténticos (H0) o fabricados/adversariales (H1). El módulo produce tres artefactos: (1) modelos KDE calibrados por herramienta, (2) matrices de covarianza regularizadas para el clúster NLP, y (3) un archivo JSON de metadatos que asegura trazabilidad completa (cumplimiento Daubert). Utiliza aritmética determinista de enteros para indexación, conteo y partición, y un hash criptográfico exacto (SHA-256) para identificación del conjunto de datos.

#### Conceptos clave

| Concepto | Descripción | Rol en la calibración |
|---|---|---|
| **Estimación de Densidad Kernel (KDE)** | Modelo no paramétrico que reconstruye una distribución de probabilidad a partir de conteos exactos de observaciones de referencia. | Construye los modelos de verosimilitud H0 y H1 para cada herramienta forense. |
| **Bandwidth (ancho de banda)** | Alcance de suavizado determinado por un escaneo determinista sobre una cuadrícula predefinida e indexada por enteros. | Controla la resolución del modelo; se selecciona mediante búsqueda exhaustiva, no adivinación. |
| **GridSearchCV** | Algoritmo determinista y exhaustivo que evalúa cada candidato en una cuadrícula indexada por enteros usando conteos exactos de pliegues. | Garantiza la selección reproducible del bandwidth. |
| **Hipótesis H0 / H1** | H0: Contenido auténtico. H1: Contenido fabricado o modificado adversarialmente. | Las dos poblaciones de referencia contra las cuales se pesa la evidencia. |
| **Encogimiento Ledoit-Wolf** | Método de regularización determinista que calcula matrices de covarianza bien condicionadas a partir de conteos exactos de muestras enteras. | Previene la degeneración numérica en el clúster NLP al agrupar múltiples herramientas. |
| **Hash canónico SHA-256** | Huella dactilar determinista de 256 bits (un entero) de todo el conjunto de calibración. | Provee trazabilidad grado-Daubert y detección de manipulación. |
| **Z-Score** | Medición de desviación estandarizada producida por una herramienta forense. | La señal cruda escalada en enteros que alimenta los modelos de calibración. |
| **Covarianza / Precisión** | Matrices que describen la variabilidad conjunta entre herramientas y su inversa algebraica exacta. | Permite la puntuación multivariada para el clúster NLP (SDA, ACP, CLI, ROI). |
| **Metadatos de trazabilidad** | Archivo JSON que registra el hash del dataset, bandwidths seleccionados, tamaños exactos de muestra y valores de encogimiento. | El certificado de calibración requerido para admisibilidad en el tribunal. |

#### Glosario de términos técnicos

- **Calibración**: Proceso de mapear lecturas crudas del instrumento (z-scores) a una escala de probabilidad validada usando muestras de referencia conocidas.
- **Validación cruzada (CV)**: Partición del dataset en un número entero exacto de pliegues (`CV_FOLDS`) para probar la estabilidad del modelo sin desperdiciar datos.
- **Estándar Daubert**: Criterio legal que exige que los métodos científicos sean comprobables, revisados por pares, y acompañados de tasas de error conocidas y trazabilidad.
- **Aritmética determinista de enteros**: Cálculos realizados sobre conteos e índices exactos, asegurando que cada ejecución con los mismos datos produzca resultados idénticos.
- **Artefacto forense**: Cualquier objeto digital sometido a examen; en este contexto, también se refiere a los archivos de salida (modelos y metadatos).
- **Razón de verosimilitud (LR)**: Peso relativo de la evidencia, computado como la relación de probabilidades bajo H1 versus H0.
- **Clúster NLP**: Conjunto de herramientas de Procesamiento de Lenguaje Natural (SDA, ACP, CLI, ROI) cuyas salidas están correlacionadas y por tanto modeladas conjuntamente.
- **Modelo no paramétrico**: Modelo estadístico que no asume una forma matemática fija (ej. curva normal), sino que sigue la distribución exacta de los datos.
- **Regularización**: Procedimiento determinista que estabiliza matemáticamente un modelo cuando los conteos de muestra son finitos.
- **Dataset sintético**: Conjunto de referencia generado artificialmente con propiedades controladas y conocidas, usado para validar la tubería de calibración.

#### 【Scientific Note】
Dentro del marco general de VIGIA, puede encontrar terminología derivada de la **semiótica peirceana**, de los códigos de **Eco** (Umberto Eco) y de los máximas conversacionales de **Grice**. Estos términos **no son misticismo**. Funcionan exactamente como el protocolo de calibración de un sensor de laboratorio. Un termopar no "sabe mágicamente" la temperatura; produce un voltaje que adquiere sentido solo después de ser mapeado a una escala de referencia mediante una curva de calibración determinista. De igual modo, los signos de Peirce, los códigos culturales de Eco y las implicaturas conversacionales de Grice son convenciones formales para mapear señales a estados del mundo. En `fit_calibration.py`, los z-scores son voltajes sin sentido hasta que este módulo los mapea a distribuciones de referencia exactas H0 y H1. El vocabulario semiótico es, por tanto, metrológico: describe cómo una señal forense adquiere significado probatorio mediante la referencia calibrada a estándares conocidos.

---

**РУССКИЙ Section**:

### РУССКИЙ

#### Что представляет собой этот модуль?
Этот скрипт, `fit_calibration.py`, — это модуль эмпирической калибровки пакета VIGIA Forensic Suite. Его цель — обучение статистических эталонных моделей, количественно оценивающих, насколько цифровой артефакт отклоняется от подлинного содержимого. Воспринимайте его как метрологический прибор: прежде чем датчик сможет измерять давление или температуру, он должен быть откалиброван по известным эталонным образцам. Здесь «датчиком» является выходное значение z-score forensic-инструмента, а эталонными образцами — документы, заведомо известные как подлинные (H0) или сфабрикованные/состязательные (H1). Модуль производит три артефакта: (1) откалиброванные KDE-модели для каждого инструмента, (2) регуляризованные ковариационные матрицы для кластера NLP и (3) JSON-файл метаданных, обеспечивающий полную прослеживаемость (соответствие стандарту Daubert). Он использует детерминированную целочисленную арифметику для индексации, подсчёта и разбиения, а также точное криптографическое хеширование (SHA-256) для идентификации набора данных.

#### Ключевые понятия

| Понятие | Описание | Роль в калибровке |
|---|---|---|
| **Ядерная оценка плотности (KDE)** | Непараметрическая модель, восстанавливающая распределение вероятностей по точным подсчётам эталонных наблюдений. | Строит модели правдоподобия H0 и H1 для каждого forensic-инструмента. |
| **Параметр размытия (bandwidth)** | Масштаб сглаживания, определяемый детерминированным перебором по заранее заданной целочисленной сетке. | Управляет разрешением модели; выбирается исчерпывающим поиском, а не наугад. |
| **GridSearchCV** | Исчерпывающий детерминированный алгоритм, оценивающий каждого кандидата на целочисленной сетке с использованием точного числа фолдов. | Гарантирует воспроизводимый выбор параметра размытия. |
| **Гипотезы H0 / H1** | H0: Подлинное содержимое. H1: Сфабрикованное или состязательно модифицированное содержимое. | Две эталонные совокупности, на фоне которых оценивается доказательство. |
| **Сжатие Ледуа — Вульфа** | Детерминированный метод регуляризации, вычисляющий хорошо обусловленные ковариационные матрицы по точным целочисленным объёмам выборки. | Предотвращает численную вырожденность в NLP-кластере при совместном моделировании нескольких инструментов. |
| **Канонический хэш SHA-256** | 256-битный детерминированный целочисленный отпечаток всего калибровочного набора данных. | Обеспечивает прослеживаемость уровня Daubert и обнаружение подмены. |
| **Z-Score** | Стандартизированное измерение отклонения, выдаваемое forensic-инструментом. | Исходный целочисленно масштабированный сигнал, подаваемый в модели калибровки. |
| **Ковариация / Точность (Precision)** | Матрицы, описывающие совместную изменчивость инструментов и её точное алгебраическое обращение. | Обеспечивает многомерное оценивание для NLP-кластера (SDA, ACP, CLI, ROI). |
| **Метаданные прослеживаемости** | JSON-файл, регистрирующий хэш набора данных, выбранные параметры размытия, точные объёмы выборки и коэффициенты сжатия. | Калибровочный сертификат, необходимый для допустимости в суде. |

#### Глоссарий технических терминов

- **Калибровка**: Процесс отображения сырых показаний прибора (z-score) на проверенную шкалу вероятностей с использованием известных эталонных образцов.
- **Перекрёстная проверка (CV)**: Разбиение набора данных на точное целочисленное число фолдов (`CV_FOLDS`) для проверки стабильности модели без потери данных.
- **Стандарт Daubert**: Юридический критерий, требующий, чтобы научные методы были проверяемыми, рецензированы, и сопровождались известными частотами ошибок и прослеживаемостью.
- **Детерминированная целочисленная арифметика**: Вычисления над точными подсчётами и индексами, гарантирующие, что каждый запуск на одних данных даёт идентичные результаты.
- **Forensic-артефакт**: Любой цифровой объект, представленный на исследование; в данном контексте также относится к выходным файлам (моделям и метаданным).
- **Отношение правдоподобия (LR)**: Относительный вес доказательства, вычисляемый как отношение вероятностей при H1 и H0.
- **Кластер NLP**: Набор инструментов обработки естественного языка (SDA, ACP, CLI, ROI), выходы которых коррелированы и поэтому моделируются совместно.
- **Непараметрическая модель**: Статистическая модель, не предполагающая фиксированной математической формы (например, нормальной кривой), а следующая точному распределению данных.
- **Регуляризация**: Детерминированная процедура, математически стабилизирующая модель при конечных объёмах выборки.
- **Синтетический набор данных**: Искусственно сгенерированный эталонный набор с контролируемыми известными свойствами, используемый для валидации конвейера калибровки.

#### 【Scientific Note】
В рамках более широкого комплекса VIGIA вы можете встретить терминологию, восходящую к **пирсовской семиотике**, теории кодов **Эко** (Умберто Эко) и максимам коммуникации **Грайса**. Эта терминология **не является мистицизмом**. Она функционирует точно так же, как протокол калибровки лабораторного датчика. Термопара не «магически» знает температуру; она выдаёт напряжение, которое приобретает смысл только после отображения на эталонную шкалу посредством детерминированной калибровочной кривой. Аналогично знаки Пирса, культурные коды Эко и разговорные импликатуры Грайса являются формальными конвенциями для отображения сигналов на состояния мира. В `fit_calibration.py` z-scores — это бессмысленные напряжения до тех пор, пока этот модуль не отобразит их на точные эталонные распределения H0 и H1. Семиотический словарь следовательно метрологичен: он описывает, как forensic-сигнал приобретает доказательственное значение через калиброванную ссылку на известные стандарты.

---

**中文 Section**:

### 中文

#### 本模块是什么？
本脚本 `fit_calibration.py` 是 VIGIA 取证套件的经验校准引擎。其目的在于训练统计参考模型，以量化数字取证工件偏离真实内容的程度。可将其视为一种计量仪器：在传感器能够测量压力或温度之前，必须使用已知参考样本对其进行校准。此处，“传感器”即为取证工具输出的 z-score，而参考样本则是已被确认为真实（H0）或伪造/对抗性（H1）的文档。本模块产出三类取证工件：(1) 按工具校准的 KDE 模型；(2) 面向 NLP 工具簇的 Ledoit-Wolf 正则化协方差矩阵；(3) 记录完整可追溯性（符合 Daubert 标准）的元数据 JSON 文件。该模块采用确定性整数运算进行索引、计数与分区，并使用精确的加密哈希算法 SHA-256 对数据集进行唯一标识。

#### 核心概念

| 概念 | 说明 | 在校准中的作用 |
|---|---|---|
| **核密度估计 (KDE)** | 一种非参数模型，依据参考观测的精确计数重建概率分布。 | 为每个取证工具构建 H0 与 H1 的似然模型。 |
| **带宽 (Bandwidth)** | 通过对预定义的整数索引网格进行确定性扫描而确定的平滑范围。 | 控制模型分辨率；由穷举网格搜索选定，非主观猜测。 |
| **网格搜索交叉验证 (GridSearchCV)** | 一种确定性穷举算法，在整数索引网格上评估每个候选参数，并使用精确的整数折数。 | 保证带宽选择的可复现性。 |
| **H0 / H1 假设** | H0：真实内容。H1：伪造或经对抗性修改的内容。 | 用以衡量证据权重的两组参考总体。 |
| **Ledoit-Wolf 收缩** | 一种确定性正则化方法，基于精确的整数样本计数计算良态协方差矩阵。 | 在联合建模多个 NLP 工具时防止数值退化。 |
| **SHA-256 规范哈希** | 对整个校准数据集生成的 256 位确定性整数指纹。 | 提供符合 Daubert 标准的可追溯性与篡改检测。 |
| **Z-Score** | 取证工具产出的标准化偏差测量值。 | 输入校准模型的原始整数尺度信号。 |
| **协方差 / 精度矩阵** | 描述工具间联合变异性的矩阵及其精确代数逆矩阵。 | 实现对 NLP 工具簇（SDA、ACP、CLI、ROI）的多变量评分。 |
| **可追溯性元数据** | JSON 文件，记录数据集哈希、所选带宽、精确样本量及收缩系数。 | 法庭可采性所需的校准证书。 |

#### 技术术语表

- **校准 (Calibration)**：使用已知参考样本，将仪器原始读数（z-score）映射到
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
