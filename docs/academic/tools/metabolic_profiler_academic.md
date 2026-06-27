<!--
VIGIA Academic Documentation
Module: ef35ef9d
Batch ID: vigia-doc-0164-ef35ef9d
Generated: 2026-05-20T14:56:47.879913+00:00
-->

# ENGLISH

## What Is This Module?
The `metabolic_profiler.py` module is a forensic instrument within the VIGÍA framework. It treats every digital artifact as a biological specimen whose "health" is determined not by its outward appearance (file content), but by its *metabolism*—the exact quantity of discrete computational cycles it demands to be parsed, expanded, and structured.

The governing axiom is physical: **obfuscation always costs cycles**. An adversary may falsify what a file appears to contain, but cannot violate the conservation of computational work. By measuring deterministic integer metrics—parse steps, nesting depth, and object expansion counts—this module detects pathologies such as parser bombs and structural obfuscation without relying on semantic interpretation.

## Key Concepts

| Concept | Scientific Definition | Operational Role |
|---|---|---|
| **Metabolic Signature** | An immutable, audit-proof record quantifying the exact integer count of operations required to ingest and expand a digital artifact. | Serves as the deterministic "fingerprint" of computational cost. |
| **Metabolic Profiler** | The analytical engine that executes controlled parsing and records integer-valued resource expenditure. | Compares observed integer costs against deterministic baselines to flag anomalies. |
| **Parser Bomb** | A malicious artifact designed to trigger exponential object instantiation during parsing, causing denial-of-service via CPU or memory exhaustion. | Identified when the integer parse-cost exceeds the `PARSE_COST_BASELINE` threshold. |
| **Obfuscation** | Adversarial transformation of a payload that preserves functional behavior while increasing structural complexity. | Revealed by integer cycle counts that are disproportionately high relative to payload entropy. |
| **Efficiency Baseline** | A deterministic integer ratio (`output_size / input_size`) defining the upper bound of acceptable metabolic efficiency for benign artifacts. | Triggers an alert if integer numerator exceeds denominator-scaled ceiling. |
| **Parse Cost Baseline** | A strict integer ceiling on the number of discrete parsing operations permitted for a given format. | Absolute deterministic limit; any integer overflow signals attack. |
| **Expected Depth** | The integer maximum of permissible nesting layers (e.g., JSON objects within objects) for a well-formed artifact. | Breaches indicate structural abuse or 逻辑断裂 (logical fracture). |
| **Deterministic Integer Arithmetic** | The exclusive use of whole-number mathematics for all measurements and thresholds. | Guarantees bit-wise reproducibility across platforms and eliminates rounding-based non-determinism. |

## Glossary

- **Artifact** — Any digital object submitted for forensic examination (e.g., a file, packet, or memory segment).
- **Baseline** — A reference integer measurement empirically derived from a population of known-benign specimens.
- **Cycle** — An atomic, indivisible unit of processor work; counted as a non-negative integer.
- **Immutable Profile** — A read-only record generated after profiling, ensuring evidentiary integrity.
- **Logical Fracture (逻辑断裂)** — A deterministic deviation between expected communication structure and observed computational reality.
- **Obfuscation** — The deliberate inflation of structural complexity to mask malicious intent.
- **Parser** — The software component responsible for lexical and syntactic decomposition of an artifact.
- **Parser Bomb** — An input crafted to cause catastrophic consumption of parsing resources.

## Scientific Note
> **【Scientific Note】Semiotics as Sensor Physics, Not Mysticism**
>
> References to Peirce, Eco (艾柯), and Grice (格赖斯) within forensic signaling frameworks are sometimes mistaken for metaphysical speculation. They are not. Semiotics functions here as a **sensor calibration model**.
>
> Consider a spectroscope: it does not "believe" in color, nor does it interpret emotion. It decomposes electromagnetic radiation into discrete, deterministic wavelengths according to physical laws. Likewise, Peircean sign theory, Eco's codes, and Grice's maxims of conversation provide the *expected transmission function* for structured communication. When an artifact violates these maxims—when it says too little, too much, or in the wrong order—it exerts a **physical stress** on the parser. The Metabolic Profiler measures that stress as an integer cost. The semiotic framework names the deviation; the integer arithmetic proves it. There is no mysticism, only measurable resistance in the channel.

## Procedures
- **Profiling Procedure (`profile`)**: Receives the file system path of an artifact. Executes deterministic integer-count parsing. Returns an immutable Metabolic Signature.
- **Integration Procedure (`integrate_metabolic_profiler`)**: Inserts the Metabolic Profiler into the VIGÍA signal routing pipeline, ensuring all ingress artifacts undergo metabolic screening before semantic analysis.

---

# ESPAÑOL

## ¿Qué es este módulo?
El módulo `metabolic_profiler.py` es un instrumento forense dentro del marco VIGÍA. Trata cada artefacto digital como un espécimen biológico cuyo "estado" no se determina por su apariencia externa (contenido del archivo), sino por su *metabolismo*: la cantidad exacta de ciclos computacionales discretos que exige para ser analizado, expandido y estructurado.

El axioma rector es físico: **la ofuscación SIEMPRE cuesta ciclos**. Un adversario puede falsificar lo que un archivo parece contener, pero no puede violar la conservación del trabajo computacional. Al medir métricas enteras deterministas—pasos de análisis, profundidad de anidamiento y conteos de expansión de objetos—este módulo detecta patologías como bombas del analizador y ofuscación estructural sin recurrir a la interpretación semántica.

## Conceptos clave

| Concepto | Definición científica | Rol operacional |
|---|---|---|
| **Firma Metabólica** | Registro inmutable y auditado que cuantifica el conteo entero exacto de operaciones requeridas para ingerir y expandir un artefacto digital. | Sirve como la "huella dactilar" determinista del costo computacional. |
| **Perfilador Metabólico** | Motor analítico que ejecuta análisis controlado y registra el gasto de recursos en valores enteros. | Compara costos enteros observados contra líneas base deterministas para señalar anomalías. |
| **Bomba del Analizador** | Artefacto malicioso diseñado para desencadenar instanciación exponencial de objetos durante el análisis, causando denegación de servicio por agotamiento de CPU o memoria. | Identificada cuando el costo entero de análisis excede el umbral `PARSE_COST_BASELINE`. |
| **Ofuscación** | Transformación adversarial de una carga útil que preserva el comportamiento funcional mientras aumenta la complejidad estructural. | Revelada por conteos enteros de ciclos desproporcionadamente altos respecto a la entropía de la carga. |
| **Línea Base de Eficiencia** | Relación entera determinista (`tamaño_salida / tamaño_entrada`) que define el límite superior de eficiencia metabólica aceptable para artefactos benignos. | Genera una alerta si el numerador entero excede el techo escalado por el denominador. |
| **Línea Base de Costo de Análisis** | Techo entero estricto sobre el número de operaciones discretas de análisis permitidas para un formato dado. | Límite determinista absoluto; cualquier desbordamiento entero señala un ataque. |
| **Profundidad Esperada** | Máximo entero de capas de anidamiento permisibles (p. ej., objetos JSON dentro de objetos) para un artefacto bien formado. | Su incumplimiento indica abuso estructural o fractura lógica. |
| **Aritmética Entera Determinista** | Uso exclusivo de matemáticas de números enteros para todas las mediciones y umbrales. | Garantiza reproducibilidad bit a bit entre plataformas y elimina la no-determinación por redondeo. |

## Glosario

- **Artefacto** — Cualquier objeto digital sometido a examen forense (p. ej., un archivo, paquete de red o segmento de memoria).
- **Línea base** — Medición de referencia entera derivada empíricamente de una población de especímenes benignos conocidos.
- **Ciclo** — Unidad atómica e indivisible de trabajo del procesador; contada como un entero no negativo.
- **Perfil inmutable** — Registro de solo lectura generado tras el perfilado, que asegura la integridad probatoria.
- **Fractura lógica** — Desviación determinista entre la estructura de comunicación esperada y la realidad computacional observada.
- **Ofuscación** — Inflación deliberada de la complejidad estructural para enmascarar intención maliciosa.
- **Analizador (Parser)** — Componente software responsable de la descomposición léxica y sintáctica de un artefacto.
- **Bomba del analizador** — Entrada diseñada para causar consumo catastrófico de recursos del analizador.

## Nota científica
> **【Nota Científica】La semiótica como física del sensor, no como misticismo**
>
> Las referencias a Peirce, Eco (艾柯) y Grice (格赖斯) dentro de los marcos de señales forenses a veces se confunden con especulación metafísica. No lo son. La semiótica funciona aquí como un **modelo de calibración del sensor**.
>
> Considere un espectroscopio: no "cree" en el color, ni interpreta emociones. Descompone la radiación electromagnética en longitudes de onda discretas y deterministas según leyes físicas. Asimismo, la teoría del signo peirceana, los códigos de Eco y los máximas conversacionales de Grice proporcionan la *función de transmisión esperada* para la comunicación estructurada. Cuando un artefacto viola estas máximas—cuando dice muy poco, demasiado, o en el orden incorrecto—ejerce un **estrés físico** sobre el analizador. El Perfilador Metabólico mide ese estrés como un costo entero. El marco semiótico nombra la desviación; la aritmética entera la prueba. No hay misticismo, solo resistencia medible en el canal.

## Procedimientos
- **Procedimiento de perfilado (`profile`)**: Recibe la ruta del sistema de archivos de un artefacto. Ejecuta análisis con conteo entero determinista. Retorna una Firma Metabólica inmutable.
- **Procedimiento de integración (`integrate_metabolic_profiler`)**: Inserta el Perfilador Metabólico en la tubería de enrutamiento de señales de VIGÍA, asegurando que todos los artefactos de ingreso se sometan a cribado metabólico antes del análisis semántico.

---

# РУССКИЙ

## Что это за модуль?
Модуль `metabolic_profiler.py` — это судебный инструмент в рамках фреймворка VIGÍA. Он рассматривает каждый цифровой артефакт как биологический образец, «состояние» которого определяется не внешним видом (содержимым файла), а его *метаболизмом* — точным количеством дискретных вычислительных циклов, необходимых для его разбора, распаковки и структурирования.

Управляющий аксиом — физический: **обфускация ВСЕГДА стоит циклов**. Противник может фальсифицировать то, что файл, кажется, содержит, но не может нарушить закон сохранения вычислительной работы. Измеряя детерминированные целочисленные метрики — шаги разбора, глубину вложенности и количество расширений объектов — этот модуль выявляет патологии, такие как парсерные бомбы и структурная обфускация, не прибегая к семантической интерпретации.

## Ключевые понятия

| Понятие | Научное определение | Операционная роль |
|---|---|---|
| **Метаболическая сигнатура** | Неизменяемая, пригодная для аудита запись, количественно определяющая точное целочисленное количество операций, необходимых для поглощения и расширения цифрового артефакта. | Служит детерминированным «отпечатком» вычислительной стоимости. |
| **Метаболический профилировщик** | Аналитический движок, выполняющий контролируемый разбор и регистрирующий затраты ресурсов в целочисленных значениях. | Сравнивает наблюдаемые целочисленные затраты с детерминированными базовыми значениями для выявления аномалий. |
| **Парсерная бомба** | Вредоносный артефакт, предназначенный для запуска экспоненциального создания объектов во время разбора, вызывая отказ в обслуживании за счёт исчерпания ЦП или памяти. | Выявляется, когда целочисленная стоимость разбора превышает порог `PARSE_COST_BASELINE`. |
| **Обфускация** | Противостоящее преобразование полезной нагрузки, сохраняющее функциональное поведение при одновременном увеличении структурной сложности. | Обнаруживается по непропорционально высоким целочисленным счётчикам циклов относительно энтропии полезной нагрузки. |
| **Базовая эффективность** | Детерминированное целочисленное отношение (`размер_вывода / размер_ввода`), определяющее верхнюю границу приемлемой метаболической эффективности для доброкачественных артефактов. | Инициирует оповещение, если целочисленный числитель превышает масштабированный знаменателем потолок. |
| **Базовая стоимость разбора** | Строгий целочисленный потолок на количество дискретных операций разбора, разрешённых для данного формата. | Абсолютный детерминированный предел; любое целочисленное переполнение сигнализирует об атаке. |
| **Ожидаемая глубина** | Целочисленный максимум допустимых уровней вложенности (например, объекты JSON внутри объектов) для корректно сформированного артефакта. | Превышение указывает на структурное злоупотребление или логический разрыв. |
| **Детерминированная целочисленная арифметика** | Исключительное использование математики целых чисел для всех измерений и порогов. | Гарантирует побитовую воспроизводимость на разных платформах и устраняет недетерминизм округления. |

## Глоссарий

- **Артефакт** — Любой цифровой объект, представленный для судебного исследования (например, файл, сетевой пакет или сегмент памяти).
- **Базовое значение (Baseline)** — Эталонное целочисленное измерение, эмпирически полученное из совокупности известных доброкачественных образцов.
- **Цикл** — Атомарная, неделимая единица работы процессора; учитывается как неотрицательное целое число.
- **Неизменяемый профиль** — Запись, доступная только для чтения, созданная после профилирования и обеспечивающая доказательную целостность.
- **Логический разрыв** — Детерминированное отклонение между ожидаемой структурой коммуникации и наблюдаемой вычислительной реальностью.
- **Обфускация** — Преднамеренное наращивание структурной сложности для маскировки вредоносного замысла.
- **Парсер** — Программный компонент, отвечающий за лексический и синтаксический разбор артефакта.
- **Парсерная бомба** — Входные данные, сконструированные для вызова катастрофического потребления ресурсов парсера.

## Научное примечание
> **【Научное примечание】Семиотика как физика датчика, а не мистика**
>
> Отсылки к Пирсу, Эко (艾柯) и Грайсу (格赖斯) в рамках судебной сигнализации иногда ошибочно принимаются за метафизическую спекуляцию. Это не так. Семиотика здесь функционирует как **модель калибровки датчика**.
>
> Вспомните спектроскоп: он не «верит» в цвет и не интерпретирует эмоции. Он разлагает электромагнитное излучение на дискретные, детерминированные длины волн в соответствии с физическими законами. Аналогично, пирсовская теория знака, коды Эко и максимы Грайса задают *ожидаемую функцию передачи* для структурированной коммуникации. Когда артефакт нарушает эти максимы — говорит слишком мало, слишком много или в неправильном порядке — он оказывает **физическое напряжение** на парсер. Метаболический профилировщик измеряет это напряжение как целочисленную стоимость. Семиотическая рамка называет отклонение; целочисленная арифметика доказывает его. Никакой мистики — только измеримое сопротивление в канале.

## Процедуры
- **Процедура профилирования (`profile`)**: Принимает путь к файловой системе артефакта. Выполняет разбор с детерминированным целочисленным подсчётом. Возвращает неизменяемую Метаболическую сигнатуру.
- **Процедура интеграции (`integrate_metabolic_profiler`)**: Встраивает Метаболический профилировщик в конвейер маршрутизации сигналов VIGÍA, гарантируя, что все входящие артефакты проходят метаболическое скрининг до семантического анализа.

---

# 中文

## 这是什么模块？
`metabolic_profiler.py` 模块是 VIGÍA 框架内的一款取证仪器。它将每一个数字**取证工件**视为生物标本，其"健康状态"并非由外表（文件内容）决定，而是由其*代谢*决定——即该工件被解析、展开和结构化时所消耗的离散计算周期之精确数量。

其核心公理是物理性的：**混淆永远消耗周期**。对手可以伪造文件看似包含的内容，但无法违反计算功的守恒定律。通过测量确定性整数指标——解析步数、嵌套深度和对象展开计数——本模块无需依赖语义解释即可检测解析器炸弹（parser bombs）和结构混淆等病理现象。

## 关键概念

| 概念 | 科学定义 | 操作职能 |
|---|---|---|
| **代谢签名** | 一份不可变的、可审计的记录，量化摄取并展开一个数字取证工件所需的精确整数操作次数。 | 作为计算成本的确定性"指纹"。 |
| **代谢分析器** | 执行受控解析并以整数值记录资源消耗的分析引擎。 | 将观测到的整数成本与确定性基线进行比对，以标记异常。 |
| **解析器炸弹** | 一种旨在触发解析期间指数级对象实例化的恶意取证工件，通过耗尽 CPU 或内存导致拒绝服务。 | 当整数解析成本超过 `PARSE_COST_BASELINE` 阈值时即被识别。 |
| **混淆** | 在保留功能行为的同时增加结构复杂度的对抗性载荷变换。 | 通过相对于载荷熵而言过高的整数周期计数予以揭示。 |
| **效率基线** | 确定性整数比率（`输出大小 / 输入大小`），定义良性取证工件可接受的最大代谢效率上限。 | 若整数分子超出按分母缩放的上限，则触发警报。 |
| **解析成本基线** | 针对特定格式所允许的离散解析操作次数的严格整数上限。 | 绝对确定性极限；任何整数溢出均表明存在攻击。 |
| **预期深度** | 格式良好的取证工件的允许嵌套层数之整数最大值（例如 JSON 对象嵌套）。 | 超出该值即表明存在结构滥用或**逻辑断裂**。 |
| **确定性整数运算** | 对所有测量和阈值仅使用整数数学。 | 保证跨平台的按位可复现性，并消除基于舍入的非确定性。 |

## 术语表

- **取证工件** — 送交取证检验的任何数字对象（例如文件、网络数据包或内存段）。
- **基线** — 从已知良性样本群体中经验推导出的参考整数测量值。
- **周期** — 处理器工作的原子性、不可再分单位；以非负整数计数。
- **不可变档案** — 分析后生成的只读记录，确保证据完整性。
- **逻辑断裂** — 预期通信结构与观测到的计算现实之间的确定性偏离。
- **混淆** — 为掩盖恶意意图而故意膨胀结构复杂度的行为。
- **解析器** — 负责取证工件的词法与语法分解的软件组件。
- **解析器炸弹** — 旨在导致解析器灾难性资源消耗的输入构造。

## 【科学说明】
> **【科学说明】符号学是传感器物理学，而非神秘主义**
>
> 在取证信号框架中提及皮尔斯、艾柯与格赖斯时，有时会被误认为形而上学臆测。事实并非如此。符号学在此处充当**传感器校准模型**。
>
> 以光谱仪为例：它并不"相信"颜色，也不诠释情感。它依据物理定律将电磁辐射分解为离散的、确定性的波长。同样，皮尔斯的符号理论、艾柯的编码系统以及格赖斯的会话准则，为结构化通信提供了*预期传输函数*。当取证工件违反这些准则——说得过少、过多，或顺序错误——它便对解析器施加了一种**物理应力**。代谢分析器将该应力测量为一个整数成本。符号学框架为偏离命名；整数运算予以证明。这里没有神秘主义，只有通道中可测量的阻力。

## 程序说明
- **剖析程序 (`profile`)**：接收取证工件的文件系统路径。执行确定性整数计数解析。返回一份不可变的代谢签名。
- **集成程序 (`integrate_metabolic_profiler`)**：将代谢分析器插入 VIGÍA 信号路由管道，确保所有入口取证工件在语义分析之前先接受代谢筛查。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
