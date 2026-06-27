<!--
VIGIA Academic Documentation
Module: 09c233b0
Batch ID: vigia-doc-0037-09c233b0
Generated: 2026-05-20T14:56:47.852514+00:00
-->

# Module Documentation: `vigia/core/advanced_signal_router.py`

## ENGLISH

**What Is This Module?**

A central dispatch system (like a mail sorting room) that takes incoming digital forensic evidence (called "signals") and sends them to the correct laboratory station (analysis pipeline) based on the evidence type (artifact type). No manual sorting needed. It ensures memory samples go to the memory lab, registry items to the registry lab, etc. It avoids floating-point rounding errors by using exact integer-based arithmetic (Fraction or string) for all numeric metadata.

**Key Concepts**

| Concept | Description | Role in Forensics |
|---|---|---|
| Signal | A unit of forensic evidence ready for analysis | The item being routed |
| Artifact Type | Category of digital evidence (memory, registry, etc.) | Determines the destination lab |
| Routing Table (ROUTING_TABLE) | Deterministic lookup map | Ensures reproducible dispatch |
| Handler Instance | The specific analysis engine object | Performs the actual examination |
| Cache | Storage of initialized handlers | Avoids redundant setup; speeds up processing |
| Fraction / String | Exact numeric representation without rounding | Guarantees integrity of numeric evidence metadata |
| Deterministic Integer Arithmetic | Calculations using exact whole numbers or rational numbers | Eliminates non-reproducible rounding errors |

**Deterministic Routing Map (Excerpt)**

| Artifact Type | Destination Engine | Example Evidence |
|---|---|---|
| memory | MemoryForensicsEngine | RAM dump, pagefile |
| *(additional types)* | *(corresponding engine)* | Registry hives, disk images, etc. |

**Glossary**

- **Router**: A dispatch coordinator; not hardware, but a logical director.
- **Pipeline**: A sequential analysis workflow (e.g., extraction → parsing → reporting).
- **Handler**: An initialized software object capable of processing a specific artifact type.
- **Cache**: A temporary holding area to reuse previously prepared resources.
- **Fraction**: A rational number type representing values exactly as integer ratios (e.g., 1/3), never as approximate decimals.
- **Deterministic**: Producing the exact same output every time the same input is given, with no randomness or rounding ambiguity.
- **Signal (Forensic)**: A structured notification carrying an evidence item and its metadata.
- **UNKNOWN**: A fallback label used when an artifact type has no matching engine.

**Scientific Note**

【Scientific Note】
This module employs semiotic concepts derived from Peirce, Eco, and Grice. These terms are **not** mysticism. Think of them exactly like a sensor array: a sensor does not "interpret" meaning in a metaphysical sense; it registers a physical state and emits a structured voltage pattern. Similarly, Peirce's sign-relation, Eco's coding frames, and Grice's cooperative maxims are used here as **formal filters**—deterministic lookup rules that map an input state (artifact type) to an output channel (analysis engine). There is no ambiguity: if the input matches the rule, the route is exact, just as a thermometer's voltage corresponds to a specific temperature reading. The terminology provides a rigorous logical vocabulary; the underlying operation is pure, reproducible integer arithmetic.

---

## ESPAÑOL

**¿Qué es este módulo?**

Un sistema central de despacho (similar a una sala de clasificación de correo) que recibe evidencia digital forense entrante (llamada "señales") y la envía a la estación de laboratorio correcta (pipeline de análisis) según el tipo de evidencia (tipo de artefacto). No requiere clasificación manual. Garantiza que las muestras de memoria vayan al laboratorio de memoria, los elementos de registro al de registro, etc. Evita errores de redondeo de punto flotante usando aritmética exacta basada en enteros (Fraction o cadena de texto) para toda la metadata numérica.

**Conceptos Clave**

| Concepto | Descripción | Papel forense |
|---|---|---|
| Señal | Paquete estructurado de evidencia digital más sus metadatos | El elemento a clasificar y analizar |
| Tipo de Artefacto | Etiqueta categórica de la evidencia (p. ej., memoria, registro) | Determina qué estación de laboratorio recibe el elemento |
| ROUTING_TABLE | Tabla de consulta fija y de solo lectura que asigna etiquetas a estaciones | Garantiza reglas de envío coherentes y reproducibles |
| Instancia de Manejador | Motor analítico activo asignado a una categoría específica de evidencia | Realiza el examen científico propiamente dicho |
| Caché | Banco de memoria a corto plazo que mantiene los motores listos para reutilizar | Elimina reinicializaciones repetidas; acelera el rendimiento |
| Fracción / Cadena | Representaciones numéricas exactas mediante razones enteras o texto | Preserva la integridad de los metadatos; evita la deriva por redondeo |
| Aritmética Entera Determinista | Matemáticas que utilizan únicamente números enteros o racionales exactos | Asegura que cada decisión de enrutamiento sea perfectamente reproducible |

**Tabla de enrutamiento (ejemplo)**

| Clave de Tipo de Artefacto | Motor de Destino | Fuente de Evidencia Típica |
|---|---|---|
| memory | MemoryForensicsEngine | Volcado de RAM, archivo de hibernación |
| *(otras claves)* | *(motores correspondientes)* | Archivos de registro, capturas de red, imágenes de disco |

**Glosario**

- **AdvancedSignalRouter**: El objeto coordinador central que ejecuta la lógica de clasificación.
- **Enrutar (route)**: Dirigir una señal hacia su motor de análisis predeterminado según la clave de tipo de artefacto.
- **Lote (batch)**: Grupo de señales procesadas conjuntamente y agrupadas por destino para mayor eficiencia.
- **Manejador (handler)**: Herramienta instanciada capaz de analizar una categoría específica de artefacto digital.
- **Caché**: Mecanismo de reutilización; una vez construido un manejador, se conserva en lugar de destruirlo y reconstruirlo.
- **Fracción (Fraction)**: Tipo de dato que almacena números como razones de enteros (p. ej., 3/10), evitando las aproximaciones propias de los decimales.
- **Cadena (string)**: Representación textual de valores numéricos cuando no se requiere aritmética fraccionaria, asegurando transcripción exacta.
- **Determinista**: Sistema en el que entradas idénticas siempre producen salidas idénticas, sin aleatoriedad ni incertidumbre de redondeo.
- **UNKNOWN**: Valor de retorno predeterminado cuando un tipo de artefacto no tiene motor correspondiente en la tabla.
- **Señal**: En este contexto, una estructura de datos forense que transporta tanto el elemento de evidencia como sus metadatos descriptivos.

**Nota Científica**

【Nota Científica】
Este módulo emplea conceptos semióticos derivados de Peirce, Eco y Grice. Estos términos **no** son misticismo. Piense en ellos exactamente como en un conjunto de sensores: un sensor no "interpreta" el significado en sentido metafísico; registra un estado físico y emite un patrón de voltaje estructurado. De igual modo, la relación-signo de Peirce, los marcos de codificación de Eco y las máximas cooperativas de Grice se usan aquí como **filtros formales**—reglas de búsqueda deterministas que mapean un estado de entrada (tipo de artefacto) a un canal de salida (motor de análisis). No hay ambigüedad: si la entrada coincide con la regla, la ruta es exacta, así como el voltaje de un termómetro corresponde a una lectura de temperatura específica. La terminología aporta un vocabulario lógico riguroso; la operación subyacente es aritmética pura y reproducible con enteros.

---

## РУССКИЙ

**Что это за модуль?**

Центральная система диспетчеризации (как сортировочный зал почты), которая принимает входящие цифровые доказательства (называемые «сигналами») и направляет их в нужную лабораторную станцию (конвейер анализа) в зависимости от типа артефакта. Ручная сортировка не требуется. Обеспечивает попадание образцов памяти в лабораторию памяти, элементов реестра — в реестровую и т.д. Исключает ошибки округления с плавающей точкой, используя точную целочисленную арифметику (Fraction или строка) для всей числовой метаданных.

**Ключевые Понятия**

| Понятие | Описание простым языком | Судебная роль |
|---|---|---|
| Сигнал | Структурированный пакет цифрового доказательства вместе с метаданными | Элемент, подлежащий сортировке и анализу |
| Тип артефакта | Категорийная бирка доказательства (например, память, реестр) | Определяет, какая станция получит экспонат |
| ROUTING_TABLE | Фиксированная таблица соответствия, сопоставляющая бирки со станциями | Гарантирует неизменные, воспроизводимые правила отправки |
| Экземпляр обработчика | Активный аналитический движок, закреплённый за конкретной категорией | Выполняет непосредственное научное исследование |
| Кэш | Кратковременное хранилище, сохраняющее движки в готовом виде | Устраняет повторную инициализацию; повышает пропускную способность |
| Дробь / Строка | Точные числовые формы на основе целочисленных отношений или текста | Сохраняет целостность метаданных; исключает накопление погрешностей округления |
| Детерминистская целочисленная арифметика | Вычисления, использующие только целые числа или точные рациональные числа | Обеспечивает абсолютную воспроизводимость каждого решения о маршрутизации |

**Пример таблицы маршрутизации**

| Ключ типа артефакта | Целевой движок | Типичный источник доказательства |
|---|---|---|
| memory | MemoryForensicsEngine | Дамп ОЗУ, файл гибернации |
| *(прочие ключи)* | *(соответствующие движки)* | Кусты реестра, сетевые дампы, образы дисков |

**Глоссарий**

- **AdvancedSignalRouter**: Центральный координирующий объект, реализующий логику сортировки.
- **Маршрутизировать (route)**: Направить сигнал в предопределённый аналитический движок на основании ключа типа артефакта.
- **Пакет (batch)**: Группа сигналов, обрабатываемых совместно и сгруппированных по пунктам назначения для повышения эффективности.
- **Обработчик (handler)**: Созданный экземпляр инструмента, способного разбирать и анализировать один конкретный вид цифрового артефакта.
- **Кэш**: Механизм повторного использования; после создания обработчик сохраняется, а не уничтожается и пересоздаётся.
- **Дробь (Fraction)**: Тип данных, хранящий числа как отношение целых чисел, исключая приближения десятичных дробей.
- **Детерминистский**: Дающий точно такой же результат при тех же входных данных, без случайности или неоднозначности округления.
- **Сигнал (криминалистический)**: Структурированное уведомление, несущее элемент доказательства и его метаданные.
- **UNKNOWN**: Метка-запасной вариант, когда тип артефакта не имеет подходящего обработчика.

**Научное Примечание**

【Научное Примечание】
Этот модуль использует семиотические концепции, восходящие к Пирсу, Эко и Грайсу. Эти термины **не** являются мистицизмом. Воспринимайте их точно так же, как массив датчиков: датчик не «интерпретирует» смысл в метафизическом смысле; он регистрирует физическое состояние и выдает структурированный шаблон напряжения. Аналогично, отношение знака у Пирса, кодировочные рамки Эко и кооперативные максимы Грайса используются здесь как **формальные фильтры**—детерминистские правила поиска, отображающие входное состояние (тип артефакта) на выходной канал (аналитический движок). Нет никакой двусмысленности: если вход совпадает с правилом, маршрут точен, точно так же, как напряжение термометра соответствует конкретному показанию температуры. Терминология обеспечивает строгий логический словарь; лежащая в основе операция — чистая воспроизводимая целочисленная арифметика.

---

## 中文

**这是什么模块？**

一个中央调度系统（类似于邮件分拣室），接收传入的数字取证证据（称为"信号"），并根据证据类型（取证工件类型）将其发送至正确的实验室工作站（分析流水线）。无需手动分拣。确保内存样本进入内存实验室，注册表项进入注册表实验室，等等。所有数值元数据均使用基于整数的精确算术（分数/字符串）表示，彻底避免浮点舍入误差。

**核心概念**

| 概念 | 通俗描述 | 取证作用 |
|---|---|---|
| 信号 | 携带取证工件及其元数据的结构化数字证据包 | 待分拣与分析的项目 |
| 取证工件类型 | 证据的类别标签（如内存、注册表等） | 决定哪个实验室工作站接收该项目 |
| 路由表 (ROUTING_TABLE) | 将标签映射到工作站的固定只读查找表 | 保证一致且可复现的调度规则 |
| 处理器实例 | 分配给特定证据类别的活跃分析引擎 | 执行实际的科学检验 |
| 缓存 | 保持引擎就绪以供复用的短期存储区域 | 消除重复初始化；提升吞吐量 |
| 分数/字符串 | 基于整数比或文本的精确数值表示 | 保护元数据完整性；防止舍入漂移 |
| 确定性整数算术 | 仅使用整数或精确有理数的数学运算 | 确保每个路由决策完全可复现 |

**路由映射示例**

| 取证工件类型键 | 目标引擎 | 典型证据来源 |
|---|---|---|
| memory | MemoryForensicsEngine | 内存转储、休眠文件 |
| *(其他键)* | *(对应引擎)* | 注册表配置单元、网络捕获、磁盘镜像 |

**术语表**

- **路由器 (Router)**：逻辑调度协调器，而非物理硬件。
- **流水线 (Pipeline)**：顺序分析工作流程。
- **处理器 (Handler)**：已初始化的、能够处理特定取证工件类型的对象。
- **缓存 (Cache)**：临时保存区域，用于复用先前准备好的资源。
- **分数 (Fraction)**：有理数类型，以整数比形式精确表示数值。
- **确定性 (Deterministic)**：在相同输入下始终产生完全相同的输出，无任何随机性或舍入歧义。
- **信号 (取证领域)**：携带取证工件及其元数据的结构化通知。
- **UNKNOWN**：当取证工件类型无匹配引擎时使用的回退标签。
- **逻辑断裂**：规则与输入之间的不匹配状态（本模块中表现为返回"UNKNOWN"）。

**科学说明**

【科学说明】
本模块采用源自皮尔斯、艾柯与格赖斯的符号学术语。这些术语**并非**神秘主义。请将其理解为传感器阵列：传感器不会在形而上学意义上"解释"含义；它仅记录物理状态并输出结构化电压模式。同样地，皮尔斯的符号关系、艾柯的编码框架以及格赖斯的合作原则，在本模块中充当**形式化过滤器**——即确定性查找规则，将输入状态（取证工件类型）映射至输出通道（分析引擎）。这里不存在歧义：若输入符合规则，路由结果即精确确定，正如温度计电压对应特定温度读数。该术语体系提供了严密的逻辑词汇；其底层运算为纯粹、可复现的整数算术。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
