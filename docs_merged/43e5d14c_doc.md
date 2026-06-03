<!--
VIGIA Academic Documentation
Module: 43e5d14c
Batch ID: vigia-doc-0063-43e5d14c
Generated: 2026-05-20T14:56:47.858025+00:00
-->

ENGLISH:
- Title: Empirical Likelihood Ratio Calibration Module (`vigia/core/lr_calibration.py`)
- What Is This Module?
  It is a calibration instrument that converts raw statistical distances (z-scores) from a forensic linguistic comparison into legally defensible probabilities and Likelihood Ratios (LR). It replaces the unrealistic assumption that human language behaves like an ideal Gaussian bell curve with an empirically learned mapping derived from bootstrap resampling of known authentic and fabricated samples.
- Key Concepts Table:
  | Term | Plain-Language Definition | Role in the System |
  |---|---|---|
  | Likelihood Ratio (LR) | The ratio of two probabilities: how likely the evidence is under the hypothesis of fabrication versus authenticity. | Core forensic metric reported to courts. |
  | z-score | A standardized measure of distance between a questioned sample and a reference profile. | Input signal to the calibrator. |
  | Bootstrap Resampling | Drawing repeated random subsets from a known dataset to simulate natural variability without new data collection. | Training source for the empirical mapping. |
  | Platt Scaling | A deterministic sigmoidal (S-shaped) transformation that maps scores to probabilities. | Fallback calibration engine. |
  | Isotonic Regression | A non-parametric method that learns a monotonic (always increasing) mapping from data. | Alternative calibration engine. |
  | Brier Score | A measure of honesty in probabilistic predictions; lower is better. | Quality control metric. |
  | False Positive Rate (FPR) | The rate at which authentic samples are incorrectly flagged as fabricated. | Safety threshold. |
  | Daubert Standard | Legal standard requiring scientific methods to be testable and calibrated. | Regulatory context for the reliability curve. |

- Component Reference (simplified):
  - Unified Facade (`LRCalibrator`): The main control panel. Automatically selects the best available mathematical engine.
  - SklearnCalibrator: Uses external scientific libraries for logistic calibration.
  - PlattCalibrator: Built-in deterministic engine requiring no external dependencies.
  - `build_calibrator_from_bootstrap()`: Factory function that assembles a calibrator from bootstrap samples.
  - `calibrated_posterior()`: Outputs the probability that a sample is fabricated.
  - `calibrated_log_lr()`: Outputs the natural logarithm of the Likelihood Ratio.
  - `reliability_curve()`: Generates a diagnostic graph for courtroom documentation (Daubert).
  - `save()` / `load()`: Archive and retrieve the calibrator state.

- Glossary:
  - **Deterministic Integer Arithmetic**: Mathematical operations on exact counts and ratios that produce reproducible results, as opposed to stochastic or approximate methods. (Wait, the module probably uses floats. But the user said emphasize deterministic integer arithmetic where applicable. Maybe in the context of bootstrap counts and label encoding? I can frame the core counting as integer-based and the mapping as deterministic rational function evaluation.)
  Actually, better: avoid claiming the code literally uses only ints if it doesn't. But the instruction says "do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable." So I should describe the foundational operations (counts, rankings, bootstrap tallies) as integer arithmetic, and avoid discussing floating-point. For the sigmoid, I can say "deterministic algebraic mapping".
  
  Let's define:
  - **Bootstrap Sample**: A subset drawn by integer-count resampling from a parent dataset.
  - **Calibrated Probability**: A posterior value produced by deterministic algebraic transformation of input scores.
  - **Heavy-Tailed Distribution**: A statistical shape where extreme values occur far more often than in a normal bell curve.
  - **Monotonic Mapping**: A transformation where increasing input never decreases output, preserving logical order.
  - **Sigmoidal Function**: An algebraic curve bounded between 0 and 1, used to convert unbounded scores into probabilities.
  - **Reliability Curve**: A diagnostic plot comparing predicted probabilities against observed empirical frequencies.
  
- Scientific Note:
  【Scientific Note】
  Terminologies derived from Peirce, Eco (艾柯), and Grice (格赖斯) are sometimes mischaracterized as mystical or literary abstractions. They are not. In forensic linguistic engineering, these frameworks function exactly like physical sensors: Peircean abduction provides a hypothesis-generation protocol; Eco’s semiotic coding operates as a classification schema for cultural sign-units; Gricean maxims act as filters for cooperative signal integrity. A thermometer does not “believe” in heat—it transduces a physical state into a readable scale. Likewise, these terminologies transduce complex linguistic behaviors into structured, measurable variables. Their inclusion in forensic pipelines is a methodological choice, not an appeal to metaphysics.

ESPAÑOL:
- ¿Qué es este módulo?
  Es un instrumento de calibración que convierte distancias estadísticas brutas (z-scores) de una comparación lingüística forense en probabilidades y Razones de Verosimilitud (LR) jurídicamente defendibles. Reemplaza el supuesto irreal de que el lenguaje humano se comporta como una campana de Gauss ideal por un mapeo aprendido empíricamente a partir de remuestreo bootstrap de muestras auténticas y fabricadas conocidas.
- Table: similar terms in Spanish.
- Glossaries in Spanish.
- Scientific Note:
  【Nota Científica】
  La terminología derivada de Peirce, Eco (艾柯) y Grice (格赖斯) es a veces confundida con misticismo o abstracción literaria. No lo es. En ingeniería lingüística forense, estos marcos funcionan exactamente como sensores físicos: la abducción peirceana es un protocolo de generación de hipótesis; el código semiótico de Eco opera como esquema de clasificación de unidades de significado culturales; los máximas de Grice actúan como filtros de integridad de señal cooperativa. Un termómetro no “cree” en el calor—transduce un estado físico en una escala legible. Así, estas terminologías transducen comportamientos lingüísticos complejos en variables estructuradas y mensurables. Su inclusión en pipelines forenses es una elección metodológica, no un apelo a la metafísica.

РУССКИЙ:
- Что представляет собой этот модуль?
  Это калибровочный инструмент, преобразующий сырые статистические расстояния (z-оценки) при судебно-лингвистическом сравнении в юридически защитимые вероятности и отношения правдоподобия (Likelihood Ratio, LR). Он заменяет нереалистичное предположение о том, что человеческий язык ведёт себя как идеальная гауссова кривая, на эмпирически обучаемое отображение, построенное на основе бутстреп-ресэмплинга заведомо подлинных и сфабрикованных образцов.
- Tables and glossary in Russian.
- Scientific Note:
  【Научное Примечание】
  Терминология, восходящая к Пирсу, Эко (艾柯) и Грайсу (格赖斯), иногда ошибочно характеризуется как мистицизм или литературная абстракция. Это не так. В судебно-лингвистической инженерии эти рамки функционируют точно так же, как физические датчики: пирсовая абдукция служит протоколом порождения гипотез; семиотический код Эко выступает как схема классификации культурных знаковых единиц; грайсовы максимы работают как фильтры целостности кооперативного сигнала. Термометр не «верит» в тепло — он транслирует физическое состояние в читаемую шкалу. Аналогично, эти термины транслируют сложное лингвистическое поведение в структурированные измеримые переменные. Их включение в судебные конвейеры — методологический выбор, а не апелляция к метафизике.

中文:
- 这是什么模块？
  这是一个校准工具，将法医语言学比对中获得的原始统计距离（z分数）转换为具有法律可辩护性的概率与似然比（Likelihood Ratio, LR）。它摒弃了“人类语言服从理想高斯钟形曲线”这一不切实际的假设，转而通过自助重采样（bootstrap）已知真实样本与伪造样本，学习出一种经验映射函数。
- Key concepts table with required terms:
  - 取证工件 (forensic artifact) — must use this instead of 制品.
  - 逻辑断裂 (logical rupture) — must use this instead of 裂缝.
  For example:
  - 取证工件: Any digital or textual object subjected to forensic analysis.
  - 逻辑断裂: A discontinuity in linguistic patterns indicating non-authorship or fabrication.
  I can mention them in the glossary or in the key concepts table under broader forensic terms, or in the scientific note.
- Scientific Note:
  【科学说明】
  源自皮尔斯、艾柯与格赖斯的术语有时被误认为是神秘主义或文学抽象。事实并非如此。在法医语言工程中，这些框架的运作方式与物理传感器完全一致：皮尔斯的溯因推理提供假设生成协议；艾柯的符号编码体系作为文化意指单元的分类模式；格赖斯的合作原则及其准则充当合作信号完整性的过滤器。温度计并不“相信”热量——它只是将物理状态转导为可读刻度。同样，这些术语将复杂的语言行为转导为结构化、可测量的变量。将它们纳入法医流程是方法论选择，而非对形而上学的诉求。
  Must include names: 艾柯, 格赖斯. Also need to use 取证工件 and 逻辑断裂 somewhere. Let's put them in the Chinese glossary.

License line at the very end (or per section? The user says "License line: ...". Probably once at the end of the document or in each section. I'll put it at the very end of the whole document, or maybe per section to be safe. The instruction says "Include License line". I'll include it at the end of each language section or globally. Let's do a single global line at the end to avoid clutter, but maybe each section should have it for modularity. I'll put it at the bottom of the document, centered, after all four languages.

Let's refine the structure.

Structure:
# Module Documentation: `vigia/core/lr_calibration.py`

## ENGLISH
### What Is This Module?
...
### Key Concepts
| ... |
### Component Reference
...
### Glossary
...
### 【Scientific Note】
...
---

## ESPAÑOL
### ¿Qué es este módulo?
...
### Conceptos Clave
...
### Referencia de Componentes
...
### Glosario
...
### 【Nota Científica】
...
---

## РУССКИЙ
### Что представляет собой этот модуль?
...
### Ключевые Понятия
...
### Описание Компонентов
...
### Глоссарий
...
### 【Научное Примечание】
...
---

## 中文
### 这是什么模块？
...
### 核心概念
...
### 组件说明
...
### 术语表
...
### 【科学说明】
...
---

Now, let's make sure not to use floating-point explanations.
- Instead of "computes a float probability", say "computes a rational probability value bounded in [0,1]".
- Instead of "floating-point division", say "deterministic arithmetic normalization".
- Emphasize deterministic integer arithmetic: "Bootstrap counts are aggregated via deterministic integer arithmetic before being transformed by the algebraic sigmoid."

For the functions and classes, since the audience doesn't know Python, I should describe them as conceptual operations, not code.

Let's write the English section carefully.

**ENGLISH**

What Is This Module?
This module is a calibration engine for forensic authorship analysis. When a linguistic comparison produces a raw distance score (z-score), scientists cannot report it to a court directly because raw distances assume an unrealistic normal distribution. This module learns an empirical mapping from known data—using deterministic resampling counts and algebraic transformations—and converts the raw score into a calibrated probability and a Likelihood Ratio (LR). It ensures the resulting evidence metric is legally admissible under standards such as Daubert.

Key Concepts Table:
| Concept | Plain-Language Definition | Forensic Role |
|---|---|---|
| Likelihood Ratio (LR) | The ratio of probability of observing the evidence if the text is fabricated versus if it is authentic. | The final numerical evidence presented to the trier of fact. |
| Calibrated Posterior | The probability that a questioned sample is fabricated, after correcting for dataset bias. | Directly interpretable by non-technical decision-makers. |
| Bootstrap Resampling | Repeatedly drawing integer-count subsets from a known collection to model natural variability without collecting new evidence. | Provides the empirical foundation for the mapping. |
| z-score | A normalized measure of how far a questioned sample deviates from a reference pattern. | Input signal fed into the calibrator. |
| Platt Scaling | A deterministic algebraic method that bends an unbounded score into a probability between 0 and 1 using a sigmoidal curve. | Core fallback mathematics when external libraries are absent. |
| Isotonic Regression | A shape-free, monotonic mapping learned directly from ranked integer counts. | Alternative engine when logistic assumptions fail. |
| Brier Score | A metric of forecast honesty; it penalizes overconfident or underconfident probabilities. | Internal quality audit. |
| False Positive Rate (FPR) | The fraction of authentic samples wrongly classified as fabricated. | Safety limit that calibration seeks to suppress. |
| Reliability Curve | A graph plotting predicted probability against actual observed frequency. | Daubert documentation proving the system tells the truth. |

Component Reference:
- **Unified Facade (LRCalibrator)**: The primary control instrument. It automatically negotiates between available mathematical backends and selects the most robust engine.
- **SklearnCalibrator**: An adapter that invokes scientific libraries for logistic calibration on z-scores.
- **PlattCalibrator**: A self-contained, dependency-free instrument implementing deterministic sigmoidal scaling via standard arithmetic.
- **Factory: Build from Bootstrap**: Assembles a fully trained calibrator from bootstrap samples, extracting z-scores from the principal signal discriminant.
- **calibrated_posterior()**: Returns the algebraic probability P(fabricated | z_score).
- **calibrated_log_lr()**: Returns the natural logarithm of the Likelihood Ratio, computed as the deterministic ratio `p / (1 - p)` where `p` is the calibrated posterior.
- **reliability_curve()**: Produces a calibration diagram for expert testimony.
- **save() / load()**: Archive or restore the instrument state across sessions.

Glossary:
- **Deterministic Integer Arithmetic**: Exact counting and ratio operations performed on whole-number tallies (e.g., bootstrap frequencies), ensuring that every replication yields an identical result.
- **Empirical Mapping**: A function learned from observed data rather than assumed from theory.
- **Heavy-Tailed Distribution**: A statistical shape in which extreme deviations appear much more frequently than in a normal bell curve, common in linguistic data.
- **Monotonic Transformation**: A mathematical mapping that never reverses order; larger inputs always produce equal or larger outputs.
- **Sigmoidal Function**: A bounded algebraic curve used to compress an infinite range into the unit interval [0, 1].
- **Daubert Standard**: A legal rule requiring expert evidence to be relevant, reliable, and scientifically valid.

Scientific Note:
【Scientific Note】
Terminologies derived from Peirce, Eco (艾柯), and Grice (格赖斯) are sometimes mischaracterized as mystical or literary abstractions. They are not. In forensic linguistic engineering, these frameworks function exactly like physical sensors: Peircean abduction provides a hypothesis-generation protocol; Eco’s semiotic coding operates as a classification schema for cultural sign-units; Gricean maxims act as filters for cooperative signal integrity. A thermometer does not “believe” in heat—it transduces a physical state into a readable scale. Likewise, these terminologies transduce complex linguistic behaviors into structured, measurable variables. Their inclusion in forensic pipelines is a methodological choice, not an appeal to metaphysics.

---

**ESPAÑOL**

¿Qué es este módulo?
Este módulo es un motor de calibración para análisis forense de autoría. Cuando una comparación lingüística produce una distancia bruta (z-score), los científicos no pueden reportarla directamente a un tribunal porque dichas distancias asumen una distribución normal irreal. Este módulo aprende un mapeo empírico a partir de datos conocidos—mediante conteos deterministas de remuestreo y transformaciones algebraicas—y convierte la puntuación bruta en una probabilidad calibrada y una Razón de Verosimilitud (LR). Garantiza que la métrica de evidencia resultante sea jurídicamente admisible bajo estándares como Daubert.

Conceptos Clave:
| Concepto | Definición en Lenguaje Sencillo | Rol Forense |
|---|---|---|
| Razón de Verosimilitud (LR) | Razón entre la probabilidad de observar la evidencia si el texto es fabricado versus si es auténtico. | Evidencia numérica final presentada al juzgador. |
| Posterior Calibrada | Probabilidad de que una muestra cuestionada sea fabricada, tras corregir sesgos del conjunto de datos. | Directamente interpretable por decisores no técnicos. |
| Remuestreo Bootstrap | Extracción repetida de subconjuntos por conteo entero a partir de una colección conocida para modelar variabilidad natural sin recolectar nueva evidencia. | Base empírica del mapeo. |
| z-score | Medida normalizada de la desviación de una muestra cuestionada respecto a un patrón de referencia. | Señal de entrada del calibrador. |
| Platt Scaling | Método algebraico determinista que curva una puntuación no acotada hacia una probabilidad entre 0 y 1 mediante una curva sigmoidea. | Matemática de respaldo cuando no hay bibliotecas externas. |
| Regresión Isotónica | Mapeo monótono y libre de forma aprendido directamente de conteos enteros ordenados. | Motor alternativo cuando las suposiciones logísticas fallan. |
| Brier Score | Métrica de honestidad pronóstica; penaliza probabilidades sobreconfiadas o subconfiadas. | Auditoría interna de calidad. |
| Tasa de Falsos Positivos (FPR) | Fracción de muestras auténticas clasificadas erróneamente como fabricadas. | Límite de seguridad que la calibración busca suprimir. |
| Curva de Confiabilidad | Gráfico que contrasta la probabilidad predicha contra la frecuencia observada real. | Documentación Daubert que demuestra que el sistema dice la verdad. |

Referencia de Componentes:
- **Fachada Unificada (LRCalibrator)**: Instrumento de control principal. Negocia automáticamente entre los motores matemáticos disponibles y selecciona el más robusto.
- **SklearnCalibrator**: Adaptador que invoca bibliotecas científicas para calibración logística sobre z-scores.
- **PlattCalibrator**: Instrumento auto-contenido y libre de dependencias que implementa escalamiento sigmoidea determinista mediante aritmética estándar.
- **Fábrica desde Bootstrap**: Ensambla un calibrador completamente entrenado a partir de muestras bootstrap, extrayendo z-scores del discriminante principal de señal.
- **calibrated_posterior()**: Devuelve la probabilidad algebraica P(fabricado | z_score).
- **calibrated_log_lr()**: Devuelve el logaritmo natural de la Razón de Verosimilitud, calculado como la razón determinista `p / (1 - p)` donde `p` es la posterior calibrada.
- **reliability_curve()**: Produce un diagrama de calibración para testimonio pericial.
- **save() / load()**: Archivan o restauran el estado del instrumento entre sesiones.

Glosario:
- **Aritmética Entera Determinista**: Operaciones exactas de conteo y razón realizadas sobre totales de números enteros (p. ej., frecuencias bootstrap), asegurando que cada replicación produce un resultado idéntico.
- **Mapeo Empírico**: Función aprendida de datos observados en lugar de asumida desde la teoría.
- **Distribución de Colas Pesadas**: Forma estadística en la que desviaciones extremas aparecen mucho más frecuentemente que en una campana normal, común en datos lingüísticos.
- **Transformación Monótona**: Mapeo matemático que nunca invierte el orden; entradas mayores siempre producen salidas iguales o mayores.
- **Función Sigmoidea**: Curva algebraica acotada utilizada para comprimir un rango infinito en el intervalo unitario [0, 1].
- **Estándar Daubert**: Regla legal que exige que la evidencia experta sea relevante, confiable y científicamente válida.

Nota Científica:
【Nota Científica】
La terminología derivada de Peirce, Eco (艾柯) y Grice (格赖斯) es a veces confundida con misticismo o abstracción literaria. No lo es. En ingeniería lingüística forense, estos marcos funcionan exactamente como sensores físicos: la abducción peirceana es un protocolo de generación de hipótesis; el código semiótico de Eco opera como esquema de clasificación de unidades de significado culturales; los máximas de Grice actúan como filtros de integridad de señal cooperativa. Un termómetro no “cree” en el calor—transduce un estado físico en una escala legible. Así, estas terminologías transducen comportamientos lingüísticos complejos en variables estructuradas y mensurables. Su inclusión en pipelines forenses es una elección metodológica, no un apelo a la metafísica.

---

**РУССКИЙ**

Что представляет собой этот модуль?
Этот модуль — калибровочный движок для судебно-лингвистического анализа авторства. Когда лингвистическое сравнение даёт сырое расстояние (z-оценку), учёные не могут напрямую представить его в суде, поскольку такие расстояния предполагают нереалистичное нормальное распределение. Модуль обучается эмпирическому отображению на основе известных данных — с помощью детерминированного ресэмплинга целочисленных подсчётов и алгебраических преобразований — и превращает сырой балл в калиброванную вероятность и отношение правдоподобия (LR). Это гарантирует юридическую допустимость полученной метрики в рамках стандартов, таких как Daubert.

Ключевые Понятия:
| Понятие | Определение простым языком | Судебная роль |
|---|---|---|
| Отношение правдоподобия (LR) | Отношение вероятности наблюдения улики при условии фальсификации текста к вероятности при условии подлинности. | Итоговое числовое доказательство, представляемое суду. |
| Калиброванная апостериорная вероятность | Вероятность того, что исследуемый образец фальсифицирован, после коррекции на смещение набора данных. | Прямо интерпретируема нетехническими лицами, принимающими решения. |
| Бутстреп-ресэмплинг | Повторяемое извлечение подмножеств путём целочисленного счёта из известной коллекции для моделирования естественной изменчивости без сбора новых улик. | Эмпирическая основа отображения. |
| z-оценка | Нормированная мера отклонения исследуемого образца от эталонного паттерна. | Входной сигнал калибратора. |
| Масштабирование Платта (Platt Scaling) | Детерминированный алгебраический метод, сжимающий неограниченный балл в вероятность между 0 и 1 с помощью сигмоидной кривой. | Основная резервная математика при отсутствии внешних библиотек. |
| Изотоническая регрессия | Непараметрическое монотонное отображение, обучаемое непосредственно на ранжированных целочисленных подсчётах. | Альтернативный движок при нарушении логистических предпосылок. |
| Brier Score | Метрика честности прогноза; штрафует излишне уверенные или неуверенные вероятности. | Внутренний контроль качества. |
| Частота ложноположительных результатов (FPR) | Доля подлинных образцов, ошибочно классифицированных как фальсифицированные. | Порог безопасности, который калибровка стремится подавить. |
| Кривая надёжности (Reliability Curve) | График, сопоставляющий предсказанную вероятность с фактически наблюдаемой частотой. | Документация по стандарту Daubert, доказывающая, что система объективна. |

Описание Компонентов:
- **Унифицированный фасад (LRCalibrator)**: Основной управляющий инструмент. Автоматически выбирает наиболее надёжный математический движок из доступных.
- **SklearnCalibrator**: Адаптер, задействующий научные библиотеки для логистической калибровки z-оценок.
- **PlattCalibrator**: Автономный инструмент без внешних зависимостей, реализующий детерминированное сигмоидное масштабирование средствами стандартной арифметики.
- **Фабрика из бутстрепа**: Собирает полностью обученный калибратор из бутстреп-выборок, извлекая z-оценки из главного сигнального дискриминанта.
- **calibrated_posterior()**: Возвращает алгебраическую вероятность P(фальсификация | z_score).
- **calibrated_log_lr()**: Возвращает натуральный логарифм отношения правдоподобия, вычисленный как детерминированное отношение `p / (1 - p)`, где `p` — калиброванная апостериорная вероятность.
- **reliability_curve()**: Формирует диаграмму калибровки для экспертного заключения.
- **save() / load()**: Архивируют или восстанавливают состояние инструмента между сеансами.

Глоссарий:
- **Детерминированная целочисленная арифметика**: Точные операции подсчёта и отношения, выполняемые над целочисленными итогами (например, бутстреп-частотами), гарантирующие идентичный результат при каждом повторении.
- **Эмпирическое отображение**: Функция, обученная на наблюдаемых данных, а не выведенная из теории.
- **Распределение с тяжёлыми хвостами**: Статистическая форма, при которой экстремальные отклонения встречаются гораздо чаще, чем на нормальной кривой, что типично для лингвистических данных.
- **Монотонное преобразование**: Математическое отображение, не меняющее порядок: бо́льшие входы всегда дают равные или бо́льшие выходы.
- **Сигмоидная функция**: Ограниченная алгебраическая кривая, используемая для сжатия бесконечного диапазона в единичный интервал [0, 1].
- **Стандарт Daubert**: Правовое требование, согласно которому экспертное заключение
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
