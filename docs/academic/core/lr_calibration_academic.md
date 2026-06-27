<!--
VIGIA Academic Documentation
Module: 43e5d14c
Batch ID: vigia-doc-0063-43e5d14c
Generated: 2026-05-20T14:56:47.858025+00:00
-->

# Module Documentation: `vigia/core/lr_calibration.py`

## ENGLISH

### What Is This Module?
This module is a calibration engine for forensic authorship analysis. When a linguistic comparison produces a raw distance score (z-score), scientists cannot report it to a court directly because raw distances assume an unrealistic normal distribution. This module learns an empirical mapping from known data—using deterministic resampling counts and algebraic transformations—and converts the raw score into a calibrated probability and a Likelihood Ratio (LR). It ensures the resulting evidence metric is legally admissible under standards such as Daubert.

### Key Concepts

| Concept | Plain-Language Definition | Forensic Role |
|---|---|---|
| **Likelihood Ratio (LR)** | The ratio of probability of observing the evidence if the text is fabricated versus if it is authentic. | The final numerical evidence presented to the trier of fact. |
| **Calibrated Posterior** | The probability that a questioned sample is fabricated, after correcting for dataset bias. | Directly interpretable by non-technical decision-makers. |
| **Bootstrap Resampling** | Repeatedly drawing integer-count subsets from a known collection to model natural variability without collecting new evidence. | Provides the empirical foundation for the mapping. |
| **z-score** | A normalized measure of how far a questioned sample deviates from a reference pattern. | Input signal fed into the calibrator. |
| **Platt Scaling** | A deterministic algebraic method that bends an unbounded score into a probability between 0 and 1 using a sigmoidal curve. | Core fallback mathematics when external libraries are absent. |
| **Isotonic Regression** | A shape-free, monotonic mapping learned directly from ranked integer counts. | Alternative engine when logistic assumptions fail. |
| **Brier Score** | A metric of forecast honesty; it penalizes overconfident or underconfident probabilities. | Internal quality audit. |
| **False Positive Rate (FPR)** | The fraction of authentic samples wrongly classified as fabricated. | Safety limit that calibration seeks to suppress. |
| **Reliability Curve** | A graph plotting predicted probability against actual observed frequency. | Daubert documentation proving the system tells the truth. |

### Component Reference

- **Unified Facade (LRCalibrator)**: The primary control instrument. It automatically negotiates between available mathematical backends and selects the most robust engine.
- **SklearnCalibrator**: An adapter that invokes scientific libraries for logistic calibration on z-scores.
- **PlattCalibrator**: A self-contained, dependency-free instrument implementing deterministic sigmoidal scaling via standard arithmetic.
- **Factory: Build from Bootstrap**: Assembles a fully trained calibrator from bootstrap samples, extracting z-scores from the principal signal discriminant.
- **calibrated_posterior()**: Returns the algebraic probability P(fabricated | z_score).
- **calibrated_log_lr()**: Returns the natural logarithm of the Likelihood Ratio, computed as the deterministic ratio `p / (1 - p)` where `p` is the calibrated posterior.
- **reliability_curve()**: Produces a calibration diagram for expert testimony.
- **save() / load()**: Archive or restore the instrument state across sessions.

### Glossary

- **Deterministic Integer Arithmetic**: Exact counting and ratio operations performed on whole-number tallies (e.g., bootstrap frequencies), ensuring that every replication yields an identical result.
- **Empirical Mapping**: A function learned from observed data rather than assumed from theory.
- **Heavy-Tailed Distribution**: A statistical shape in which extreme deviations appear much more frequently than in a normal bell curve, common in linguistic data.
- **Monotonic Transformation**: A mathematical mapping that never reverses order; larger inputs always produce equal or larger outputs.
- **Sigmoidal Function**: A bounded algebraic curve used to compress an infinite range into the unit interval [0, 1].
- **Daubert Standard**: A legal rule requiring expert evidence to be relevant, reliable, and scientifically valid.

### 【Scientific Note】
Terminologies derived from Peirce, Eco (艾柯), and Grice (格赖斯) are sometimes mischaracterized as mystical or literary abstractions. They are not. In forensic linguistic engineering, these frameworks function exactly like physical sensors: Peircean abduction provides a hypothesis-generation protocol; Eco's semiotic coding operates as a classification schema for cultural sign-units; Gricean maxims act as filters for cooperative signal integrity. A thermometer does not "believe" in heat—it transduces a physical state into a readable scale. Likewise, these terminologies transduce complex linguistic behaviors into structured, measurable variables. Their inclusion in forensic pipelines is a methodological choice, not an appeal to metaphysics.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo es un motor de calibración para análisis forense de autoría. Cuando una comparación lingüística produce una distancia bruta (z-score), los científicos no pueden reportarla directamente a un tribunal porque dichas distancias asumen una distribución normal irreal. Este módulo aprende un mapeo empírico a partir de datos conocidos—mediante conteos deterministas de remuestreo y transformaciones algebraicas—y convierte la puntuación bruta en una probabilidad calibrada y una Razón de Verosimilitud (LR). Garantiza que la métrica de evidencia resultante sea jurídicamente admisible bajo estándares como Daubert.

### Conceptos Clave

| Concepto | Definición en Lenguaje Sencillo | Rol Forense |
|---|---|---|
| **Razón de Verosimilitud (LR)** | Razón entre la probabilidad de observar la evidencia si el texto es fabricado versus si es auténtico. | Evidencia numérica final presentada al juzgador. |
| **Posterior Calibrada** | Probabilidad de que una muestra cuestionada sea fabricada, tras corregir sesgos del conjunto de datos. | Directamente interpretable por decisores no técnicos. |
| **Remuestreo Bootstrap** | Extracción repetida de subconjuntos por conteo entero a partir de una colección conocida para modelar variabilidad natural sin recolectar nueva evidencia. | Base empírica del mapeo. |
| **z-score** | Medida normalizada de la desviación de una muestra cuestionada respecto a un patrón de referencia. | Señal de entrada del calibrador. |
| **Platt Scaling** | Método algebraico determinista que curva una puntuación no acotada hacia una probabilidad entre 0 y 1 mediante una curva sigmoidea. | Matemática de respaldo cuando no hay bibliotecas externas. |
| **Regresión Isotónica** | Mapeo monótono y libre de forma aprendido directamente de conteos enteros ordenados. | Motor alternativo cuando las suposiciones logísticas fallan. |
| **Brier Score** | Métrica de honestidad pronóstica; penaliza probabilidades sobreconfiadas o subconfiadas. | Auditoría interna de calidad. |
| **Tasa de Falsos Positivos (FPR)** | Fracción de muestras auténticas clasificadas erróneamente como fabricadas. | Límite de seguridad que la calibración busca suprimir. |
| **Curva de Confiabilidad** | Gráfico que contrasta la probabilidad predicha contra la frecuencia observada real. | Documentación Daubert que demuestra que el sistema dice la verdad. |

### Referencia de Componentes

- **Fachada Unificada (LRCalibrator)**: Instrumento de control principal. Negocia automáticamente entre los motores matemáticos disponibles y selecciona el más robusto.
- **SklearnCalibrator**: Adaptador que invoca bibliotecas científicas para calibración logística sobre z-scores.
- **PlattCalibrator**: Instrumento auto-contenido y libre de dependencias que implementa escalamiento sigmoideo determinista mediante aritmética estándar.
- **Fábrica desde Bootstrap**: Ensambla un calibrador completamente entrenado a partir de muestras bootstrap, extrayendo z-scores del discriminante principal de señal.
- **calibrated_posterior()**: Devuelve la probabilidad algebraica P(fabricado | z_score).
- **calibrated_log_lr()**: Devuelve el logaritmo natural de la Razón de Verosimilitud, calculado como la razón determinista `p / (1 - p)` donde `p` es la posterior calibrada.
- **reliability_curve()**: Produce un diagrama de calibración para testimonio pericial.
- **save() / load()**: Archivan o restauran el estado del instrumento entre sesiones.

### Glosario

- **Aritmética Entera Determinista**: Operaciones exactas de conteo y razón realizadas sobre totales de números enteros (p. ej., frecuencias bootstrap), asegurando que cada replicación produce un resultado idéntico.
- **Mapeo Empírico**: Función aprendida de datos observados en lugar de asumida desde la teoría.
- **Distribución de Colas Pesadas**: Forma estadística en la que desviaciones extremas aparecen mucho más frecuentemente que en una campana normal, común en datos lingüísticos.
- **Transformación Monótona**: Mapeo matemático que nunca invierte el orden; entradas mayores siempre producen salidas iguales o mayores.
- **Función Sigmoidea**: Curva algebraica acotada utilizada para comprimir un rango infinito en el intervalo unitario [0, 1].
- **Estándar Daubert**: Regla legal que exige que la evidencia experta sea relevante, confiable y científicamente válida.

### 【Nota Científica】
La terminología derivada de Peirce, Eco (艾柯) y Grice (格赖斯) es a veces confundida con misticismo o abstracción literaria. No lo es. En ingeniería lingüística forense, estos marcos funcionan exactamente como sensores físicos: la abducción peirceana es un protocolo de generación de hipótesis; el código semiótico de Eco opera como esquema de clasificación de unidades de significado culturales; los máximas de Grice actúan como filtros de integridad de señal cooperativa. Un termómetro no "cree" en el calor—transduce un estado físico en una escala legible. Así, estas terminologías transducen comportamientos lingüísticos complejos en variables estructuradas y mensurables. Su inclusión en pipelines forenses es una elección metodológica, no un apelo a la metafísica.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Этот модуль — калибровочный движок для судебно-лингвистического анализа авторства. Когда лингвистическое сравнение даёт сырое расстояние (z-оценку), учёные не могут напрямую представить его в суде, поскольку такие расстояния предполагают нереалистичное нормальное распределение. Модуль обучается эмпирическому отображению на основе известных данных — с помощью детерминированного ресэмплинга целочисленных подсчётов и алгебраических преобразований — и превращает сырой балл в калиброванную вероятность и отношение правдоподобия (LR). Это гарантирует юридическую допустимость полученной метрики в рамках стандартов, таких как Daubert.

### Ключевые Понятия

| Понятие | Определение простым языком | Судебная роль |
|---|---|---|
| **Отношение правдоподобия (LR)** | Отношение вероятности наблюдения улики при условии фальсификации текста к вероятности при условии подлинности. | Итоговое числовое доказательство, представляемое суду. |
| **Калиброванная апостериорная вероятность** | Вероятность того, что исследуемый образец фальсифицирован, после коррекции на смещение набора данных. | Прямо интерпретируема нетехническими лицами, принимающими решения. |
| **Бутстреп-ресэмплинг** | Повторяемое извлечение подмножеств путём целочисленного счёта из известной коллекции для моделирования естественной изменчивости без сбора новых улик. | Эмпирическая основа отображения. |
| **z-оценка** | Нормированная мера отклонения исследуемого образца от эталонного паттерна. | Входной сигнал калибратора. |
| **Масштабирование Платта (Platt Scaling)** | Детерминированный алгебраический метод, сжимающий неограниченный балл в вероятность между 0 и 1 с помощью сигмоидной кривой. | Основная резервная математика при отсутствии внешних библиотек. |
| **Изотоническая регрессия** | Непараметрическое монотонное отображение, обучаемое непосредственно на ранжированных целочисленных подсчётах. | Альтернативный движок при нарушении логистических предпосылок. |
| **Brier Score** | Метрика честности прогноза; штрафует излишне уверенные или неуверенные вероятности. | Внутренний контроль качества. |
| **Частота ложноположительных результатов (FPR)** | Доля подлинных образцов, ошибочно классифицированных как фальсифицированные. | Порог безопасности, который калибровка стремится подавить. |
| **Кривая надёжности (Reliability Curve)** | График, сопоставляющий предсказанную вероятность с фактически наблюдаемой частотой. | Документация по стандарту Daubert, доказывающая, что система объективна. |

### Описание Компонентов

- **Унифицированный фасад (LRCalibrator)**: Основной управляющий инструмент. Автоматически выбирает наиболее надёжный математический движок из доступных.
- **SklearnCalibrator**: Адаптер, задействующий научные библиотеки для логистической калибровки z-оценок.
- **PlattCalibrator**: Автономный инструмент без внешних зависимостей, реализующий детерминированное сигмоидное масштабирование средствами стандартной арифметики.
- **Фабрика из бутстрепа**: Собирает полностью обученный калибратор из бутстреп-выборок, извлекая z-оценки из главного сигнального дискриминанта.
- **calibrated_posterior()**: Возвращает алгебраическую вероятность P(фальсификация | z_score).
- **calibrated_log_lr()**: Возвращает натуральный логарифм отношения правдоподобия, вычисленный как детерминированное отношение `p / (1 - p)`, где `p` — калиброванная апостериорная вероятность.
- **reliability_curve()**: Формирует диаграмму калибровки для экспертного заключения.
- **save() / load()**: Архивируют или восстанавливают состояние инструмента между сеансами.

### Глоссарий

- **Детерминированная целочисленная арифметика**: Точные операции подсчёта и отношения, выполняемые над целочисленными итогами (например, бутстреп-частотами), гарантирующие идентичный результат при каждом повторении.
- **Эмпирическое отображение**: Функция, обученная на наблюдаемых данных, а не выведенная из теории.
- **Распределение с тяжёлыми хвостами**: Статистическая форма, при которой экстремальные отклонения встречаются гораздо чаще, чем на нормальной кривой, что типично для лингвистических данных.
- **Монотонное преобразование**: Математическое отображение, не меняющее порядок: бо́льшие входы всегда дают равные или бо́льшие выходы.
- **Сигмоидная функция**: Ограниченная алгебраическая кривая, используемая для сжатия бесконечного диапазона в единичный интервал [0, 1].
- **Стандарт Daubert**: Правовое требование, согласно которому экспертное заключение должно быть относимым, надёжным и научно обоснованным.

### 【Научное Примечание】
Терминология, восходящая к Пирсу, Эко (艾柯) и Грайсу (格赖斯), иногда ошибочно характеризуется как мистицизм или литературная абстракция. Это не так. В судебно-лингвистической инженерии эти рамки функционируют точно так же, как физические датчики: пирсовая абдукция служит протоколом порождения гипотез; семиотический код Эко выступает как схема классификации культурных знаковых единиц; грайсовы максимы работают как фильтры целостности кооперативного сигнала. Термометр не «верит» в тепло — он транслирует физическое состояние в читаемую шкалу. Аналогично, эти термины транслируют сложное лингвистическое поведение в структурированные измеримые переменные. Их включение в судебные конвейеры — методологический выбор, а не апелляция к метафизике.

---

## 中文

### 这是什么模块？
这是一个校准工具，将法医语言学比对中获得的原始统计距离（z分数）转换为具有法律可辩护性的概率与似然比（Likelihood Ratio, LR）。它摒弃了"人类语言服从理想高斯钟形曲线"这一不切实际的假设，转而通过自助重采样（bootstrap）已知真实样本与伪造样本，学习出一种经验映射函数。

### 核心概念

| 概念 | 通俗定义 | 取证作用 |
|---|---|---|
| **似然比（LR）** | 在文本被伪造的假设下观测到该证据的概率，与在文本真实的假设下观测到该证据的概率之比。 | 呈交给事实裁判者的最终数值证据。 |
| **校准后验概率** | 在修正数据集偏差后，被质疑样本属于伪造品的概率。 | 可由非技术性决策者直接解读。 |
| **自助重采样（Bootstrap）** | 通过整数计数从已知集合中反复抽取子集，以模拟自然变异性，无需收集新证据。 | 为映射函数提供经验基础。 |
| **z分数** | 衡量被质疑样本偏离参考模式程度的归一化指标。 | 输入到校准器的信号。 |
| **Platt缩放** | 一种确定性代数方法，通过S型曲线将无界得分映射到0至1之间的概率。 | 缺少外部库时的核心备用数学方法。 |
| **保序回归** | 直接从有序整数计数中学习的无形状单调映射。 | 当对数假设不成立时的备用引擎。 |
| **Brier分数** | 概率预测诚实度的度量；惩罚过度自信或信心不足的概率。 | 内部质量审计指标。 |
| **假阳性率（FPR）** | 真实样本被错误分类为伪造的比例。 | 校准寻求抑制的安全限制。 |
| **可靠性曲线** | 绘制预测概率与实际观测频率对比的图表。 | 证明系统客观的Daubert文档。 |

### 组件说明

- **统一外观（LRCalibrator）**：主控制仪器。自动在可用数学后端之间协商，选择最稳健的引擎。
- **SklearnCalibrator**：调用科学库对z分数进行逻辑校准的适配器。
- **PlattCalibrator**：无外部依赖的自包含仪器，通过标准算术实现确定性S型缩放。
- **自助法工厂**：从自助样本组装完整训练好的校准器，从主信号判别量中提取z分数。
- **calibrated_posterior()**：返回代数概率 P(伪造 | z_score)。
- **calibrated_log_lr()**：返回似然比的自然对数，计算为确定性比值 `p / (1 - p)`，其中 `p` 为校准后验概率。
- **reliability_curve()**：生成用于专家证词的校准图。
- **save() / load()**：在会话间归档或恢复仪器状态。

### 术语表

- **确定性整数运算**：对整数计数（如自助频率）执行的精确计数与比率运算，确保每次重复产生相同结果。
- **经验映射**：从观测数据中学习的函数，而非从理论假设推导。
- **重尾分布**：极端偏差出现频率远高于正态钟形曲线的统计形态，在语言数据中常见。
- **单调变换**：从不逆转顺序的数学映射；较大输入始终产生等于或较大的输出。
- **S型函数**：用于将无界范围压缩到单位区间 [0, 1] 的有界代数曲线。
- **Daubert标准**：要求专家证据具有相关性、可靠性和科学有效性的法律规则。
- **取证工件**：接受法医分析的任何数字或文本对象。
- **逻辑断裂**：语言模式中指示非作者身份或伪造的不连续性。

### 【科学说明】
源自皮尔斯、艾柯与格赖斯的术语有时被误认为是神秘主义或文学抽象。事实并非如此。在法医语言工程中，这些框架的运作方式与物理传感器完全一致：皮尔斯的溯因推理提供假设生成协议；艾柯的符号编码体系作为文化意指单元的分类模式；格赖斯的合作原则及其准则充当合作信号完整性的过滤器。温度计并不"相信"热量——它只是将物理状态转导为可读刻度。同样，这些术语将复杂的语言行为转导为结构化、可测量的变量。将它们纳入法医流程是方法论选择，而非对形而上学的诉求。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
