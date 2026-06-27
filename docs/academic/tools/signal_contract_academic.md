<!--
VIGIA Academic Documentation
Module: 26dcd8ee
Batch ID: vigia-doc-0172-26dcd8ee
Generated: 2026-05-20T14:56:47.881842+00:00
-->

## ENGLISH

### What Is This Module?
`vigia/tools/signal_contract.py` is the mandatory protocol—an interoperability contract—that every forensic instrument in the VIGÍA suite must follow when exporting its findings. It functions as a deterministic translation layer between the **Evidence Layer** (where raw digital artifacts are measured by tools such as SDA, CLI, GCI, and ACP) and the **Inference Layer** (where the LikelihoodEngine performs probabilistic reasoning).

If any tool bypasses this contract, the LikelihoodEngine receives incompatible input. This creates a **logical break** in the analytical chain, rendering any subsequent conclusion indefensible under **Daubert** standards. The module guarantees that all measurements are packaged into a single, immutable object called `SignalOutput`, using only deterministic integer arithmetic for normalization and validation. No large language model (LLM) operates at this stage; the process is fully reproducible.

### Key Concepts

| Concept | Function | Determinism Guarantee |
|---|---|---|
| **SignalOutput** | Immutable data capsule that carries a single forensic measurement from tool to engine | Schema-locked fields; no post-hoc modification |
| **SignalBuilder** | Defensive factory that constructs `SignalOutput` instances | Validates ranges, names, and numeric integrity via deterministic checks |
| **Evidence Layer** | Execution stage for forensic tools (SDA, CLI, GCI, ACP) | LLM-free; exact integer arithmetic only |
| **Inference Layer** | Consumption stage for the LikelihoodEngine | Receives strictly standardized numeric signals |
| **Report Layer** | Narrative synthesis stage | LLM is permitted only *after* numeric results are finalized; it cannot alter the signal |
| **ENFSI Scale** | Verbal category mapping for Likelihood Ratios | Deterministic lookup; no statistical re-interpretation |
| **from_raw()** | Builds `SignalOutput` from an unprocessed integer or rational observation | Computes standardized indices via deterministic integer arithmetic |
| **from_z_score()** | Wraps a pre-computed standardized index into the contract | Skips re-calculation; preserves exact input |
| **Pydantic / dataclass** | Backend validation technology | Schema enforcement is identical regardless of which backend is present |

### Glossary

- **SignalContract**: The formal interface specification that defines how forensic tools must emit data.
- **SignalOutput**: The standardized transfer object. Think of it as a labeled evidence tube with a pre-printed chain-of-custody form.
- **SignalBuilder**: The factory class that checks a tool's output for completeness and correctness before sealing the tube.
- **LikelihoodEngine**: The probabilistic inference core of VIGÍA. It only understands `SignalOutput`.
- **Daubert**: The legal standard requiring scientific reliability and relevance for expert testimony. A broken signal contract breaks Daubert compliance.
- **SDA / CLI / GCI / ACP**: Forensic sub-tools within VIGÍA. Each produces raw measurements that must be wrapped in `SignalOutput`.
- **z-score**: A deterministic standardized index indicating how many integer standard deviations an observation lies from a baseline mean.
- **ENFSI Scale**: A seven-level verbal scale (e.g., Limited Support, Moderately Strong Support) mapped deterministically from a Likelihood Ratio.
- **Evidence Layer**: The deterministic, LLM-free stratum where raw observations are converted into signals.
- **Report Layer**: The stratum where natural-language reports are generated, strictly *after* numeric inference is complete.
- **Logical break**: A discontinuity in the chain of custody caused by non-compliant data formats.

### 【Scientific Note】
Terminology inspired by **Peirce** (semiotics), **Eco** (codes of interpretation), and **Grice** (cooperative communication) is used throughout VIGÍA to describe how a forensic tool transforms a digital trace into a structured sign. This is not mysticism.

Consider a laboratory sensor: a thermocouple converts thermal energy into voltage according to a physical contract. The voltage reading is not an opinion; it is a signal. `SignalOutput` is the voltage reading of a forensic sensor. Peirce explains *why* the reading stands for something else (the underlying digital artifact); Eco explains *how* the contractual code makes that reading interpretable by the LikelihoodEngine; Grice explains *what* the tool must cooperatively disclose so that the inference engine is not misled. The contract removes ambiguity exactly as a calibrated sensor removes guesswork from measurement.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia/tools/signal_contract.py` es el protocolo obligatorio —un contrato de interoperabilidad— que todo instrumento forense del ecosistema VIGÍA debe seguir al exportar sus hallazgos. Actúa como una capa de traducción determinística entre la **Capa de Evidencia** (donde herramientas como SDA, CLI, GCI y ACP miden artefactos digitales brutos) y la **Capa de Inferencia** (donde el LikelihoodEngine realiza razonamiento probabilístico).

Si alguna herramienta omite este contrato, el LikelihoodEngine recibe datos incompatibles. Esto provoca una **ruptura lógica** en la cadena analítica, haciendo que cualquier conclusión subsiguiente sea indefendible bajo los criterios **Daubert**. El módulo garantiza que todas las mediciones se empaqueten en un objeto inmutable denominado `SignalOutput`, empleando únicamente aritmética entera determinística para la normalización y validación. Ningún modelo de lenguaje (LLM) opera en esta etapa; el proceso es completamente reproducible.

### Conceptos clave

| Concepto | Función | Garantía de determinismo |
|---|---|---|
| **SignalOutput** | Cápsula de datos inmutable que transporta una medición forense desde la herramienta hasta el motor | Campos bloqueados por esquema; sin modificación posterior |
| **SignalBuilder** | Fábrica defensiva que construye instancias de `SignalOutput` | Valida rangos, nombres e integridad numérica mediante comprobaciones deterministas |
| **Capa de Evidencia** | Etapa de ejecución de las herramientas forenses (SDA, CLI, GCI, ACP) | Sin LLM; aritmética entera exacta únicamente |
| **Capa de Inferencia** | Etapa de consumo del LikelihoodEngine | Recibe señales numéricas estrictamente estandarizadas |
| **Capa de Informe** | Etapa de síntesis narrativa | El LLM solo se permite *después* de finalizar los resultados numéricos; no puede alterar la señal |
| **Escala ENFSI** | Mapeo categórico verbal para Razones de Verosimilitud | Búsqueda determinista; sin reinterpretación estadística |
| **from_raw()** | Construye `SignalOutput` a partir de una observación entera o racional sin procesar | Calcula índices estandarizados mediante aritmética entera determinística |
| **from_z_score()** | Envuelve un índice estandarizado previamente calculado dentro del contrato | Omite el recálculo; preserva el valor exacto de entrada |
| **Pydantic / dataclass** | Tecnología backend de validación | El cumplimiento del esquema es idéntico independientemente del backend disponible |

### Glosario

- **SignalContract**: La especificación formal de interfaz que define cómo deben emitir datos las herramientas forenses.
- **SignalOutput**: El objeto de transferencia estandarizado. Piense en él como un tubo de evidencia etiquetado con un formulario de cadena de custodia preimpreso.
- **SignalBuilder**: La clase fábrica que verifica la integridad y completitud de la salida de una herramienta antes de sellar el tubo.
- **LikelihoodEngine**: El núcleo de inferencia probabilística de VIGÍA. Únicamente entiende `SignalOutput`.
- **Daubert**: El estándar legal que exige confiabilidad y relevancia científica para el testimonio de expertos. Un contrato de señales roto viola este cumplimiento.
- **SDA / CLI / GCI / ACP**: Sub-herramientas forenses de VIGÍA. Cada una produce mediciones brutas que deben envolverse en `SignalOutput`.
- **z-score**: Un índice estandarizado determinístico que indica cuántos desvíos estándar enteros separan una observación de una media basal.
- **Escala ENFSI**: Una escala verbal de siete niveles (p. ej., Apoyo limitado, Apoyo moderadamente fuerte) mapeada determinísticamente a partir de una Razón de Verosimilitud.
- **Capa de Evidencia**: El estrato determinista y libre de LLM donde las observaciones brutas se convierten en señales.
- **Capa de Informe**: El estrato donde se generan informes en lenguaje natural, estrictamente *después* de que la inferencia numérica haya concluido.
- **Ruptura lógica**: Una discontinuidad en la cadena de custodia provocada por formatos de datos no conformes.

### 【Nota Científica】
La terminología inspirada en **Peirce** (semiótica), **Eco** (códigos de interpretación) y **Grice** (comunicación cooperativa) se utiliza en VIGÍA para describir cómo una herramienta forense transforma un rastro digital en un signo estructurado. Esto no es misticismo.

Considere un sensor de laboratorio: un termopar convierte energía térmica en voltaje según un contrato físico. La lectura de voltaje no es una opinión; es una señal. `SignalOutput` es la lectura de voltaje de un sensor forense. Peirce explica *por qué* la lectura representa otra cosa (el artefacto digital subyacente); Eco explica *cómo* el código contractual hace que esa lectura sea interpretable por el LikelihoodEngine; Grice explica *qué* debe revelar cooperativamente la herramienta para que el motor de inferencia no sea inducido a error. El contrato elimina la ambigüedad exactamente igual que un sensor calibrado elimina la conjetura de la medición.

---

## РУССКИЙ

### Что представляет собой этот модуль?
`vigia/tools/signal_contract.py` — это обязательный протокол, контракт интероперабельности, которому должны следовать все судебно-экспертные инструменты экосистемы VIGÍA при экспорте результатов. Он выступает в роли детерминированного трансляционного слоя между **Уровнем доказательств** (где инструменты SDA, CLI, GCI и ACP измеряют исходные цифровые артефакты) и **Уровнем инференса** (где ядро LikelihoodEngine выполняет вероятностное рассуждение).

Если какой-либо инструмент обходит этот контракт, LikelihoodEngine получает несовместимые входные данные. Это вызывает **логический разрыв** в аналитической цепочке, делая любой последующий вывод незащитимым по критериям **Daubert**. Модуль гарантирует, что все измерения упаковываются в неизменяемый объект `SignalOutput`, причём нормализация и валидация выполняются исключительно детерминированной целочисленной арифметикой. На этом этапе не задействованы большие языковые модели (LLM); процесс полностью воспроизводим.

### Ключевые понятия

| Понятие | Функция | Гарантия детерминизма |
|---|---|---|
| **SignalOutput** | Неизменяемая капсула данных, переносящая одно судебное измерение от инструмента к ядру | Поля зафиксированы схемой; пост-хок модификация исключена |
| **SignalBuilder** | Защитная фабрика, конструирующая экземпляры `SignalOutput` | Детерминированные проверки диапазонов, имён и числовой целостности |
| **Уровень доказательств** | Этап выполнения судебных инструментов (SDA, CLI, GCI, ACP) | Без LLM; только точная целочисленная арифметика |
| **Уровень инференса** | Этап потребления данных ядром LikelihoodEngine | Получает строго стандартизированные числовые сигналы |
| **Уровень отчётности** | Этап синтеза повествовательного отчёта | LLM разрешён только *после* финализации числовых результатов; сигнал изменить нельзя |
| **Шкала ENFSI** | Словесное категориальное отображение отношения правдоподобия | Детерминированное табличное соответствие; статистическая реинтерпретация исключена |
| **from_raw()** | Создаёт `SignalOutput` из необработанного целочисленного или рационального наблюдения | Вычисляет стандартизированные индексы детерминированной целочисленной арифметикой |
| **from_z_score()** | Оборачивает ранее вычисленный стандартизированный индекс в контракт | Пропускает повторное вычисление; сохраняет точность входного значения |
| **Pydantic / dataclass** | Технология валидации на нижнем уровне | Соблюдение схемы идентично независимо от доступного бэкенда |

### Глоссарий

- **SignalContract**: Формальная спецификация интерфейса, определяющая, как судебные инструменты должны выдавать данные.
- **SignalOutput**: Стандартизированный объект передачи. Воспринимайте его как помеченную пробирку с доказательством и заранее заполненной формой цепочки сохранности.
- **SignalBuilder**: Фабричный класс, проверяющий полноту и корректность вывода инструмента перед опечатыванием пробирки.
- **LikelihoodEngine**: Ядро вероятностного инференса VIGÍA. Понимает только `SignalOutput`.
- **Daubert**: Правовой стандарт, требующий научной надёжности и актуальности для заключения эксперта. Нарушение контракта сигналов разрушает соответствие этому стандарту.
- **SDA / CLI / GCI / ACP**: Судебно-экспертные подинструменты VIGÍA. Каждый производит сырые измерения, которые должны быть обёрнуты в `SignalOutput`.
- **z-score**: Детерминированный стандартизированный индекс, показывающий, на сколько целочисленных стандартных отклонений наблюдение удалено от базового среднего.
- **Шкала ENFSI**: Семиуровневая словесная шкала (например, «ограниченная поддержка», «умеренно сильная поддержка»), детерминированно отображаемая из отношения правдоподобия.
- **Уровень доказательств**: Детерминированный слой без LLM, где исходные наблюдения превращаются в сигналы.
- **Уровень отчётности**: Слой генерации отчётов на естественном языке, строго *после* завершения числового инференса.
- **Логический разрыв**: Разрыв в цепочке сохранности, вызванный несоответствующими форматами данных.

### 【Научное Примечание】
Терминология, вдохновлённая **Пирсом** (семиотика), **Эко** (коды интерпретации) и **Грайсом** (кооперативная коммуникация), используется в VIGÍA для описания того, как судебный инструмент преобразует цифровой след в структурированный знак. Это не мистицизм.

Представьте лабораторный датчик: термопара преобразует тепловую энергию в напряжение согласно физическому контракту. Показание напряжения — не мнение; это сигнал. `SignalOutput` является показанием напряжения судебного датчика. Пирс объясняет, *почему* показание представляет нечто иное (лежащий в основе цифровой артефакт); Эко объясняет, *как* кодекс контракта делает это показание интерпретируемым для LikelihoodEngine; Грайс объясняет, *что* инструмент должен кооперативно раскрыть, чтобы ядро инференса не было введено в заблуждение. Контракт устраняет неоднозначность точно так же, как калиброванный датчик устраняет догадки из измерения.

---

## 中文

### 此模块是什么？
`vigia/tools/signal_contract.py` 是 VIGÍA 生态系统中所有取证工具在输出结果时必须遵守的强制性协议，即一种互操作性契约。它是**证据层**（由 SDA、CLI、GCI、ACP 等工具对原始数字取证工件进行测量的阶段）与**推断层**（LikelihoodEngine 执行概率推理的阶段）之间的确定性转换层。

若有任何工具绕过该契约，LikelihoodEngine 将接收到不兼容的输入。这会在分析链条中造成**逻辑断裂**，导致后续任何结论均无法在 **Daubert** 标准下得到辩护。本模块确保所有测量值都被封装进一个名为 `SignalOutput` 的不可变对象中，其标准化与验证过程仅使用确定性整数运算。此阶段不调用任何大语言模型（LLM）；整个过程完全可复现。

### 核心概念

| 概念 | 功能 | 确定性保证 |
|---|---|---|
| **SignalOutput** | 将单条取证测量值从工具运输至推理引擎的不可变数据胶囊 | 字段受模式锁定；禁止事后修改 |
| **SignalBuilder** | 构建 `SignalOutput` 实例的防御性工厂 | 通过确定性检查验证范围、名称与数值完整性 |
| **证据层** | 取证工具（SDA、CLI、GCI、ACP）的执行阶段 | 无 LLM 介入；仅使用精确整数运算 |
| **推断层** | LikelihoodEngine 消费信号的阶段 | 接收严格标准化的数字信号 |
| **报告层** | 叙述性综合报告生成阶段 | LLM 仅在数值结果最终确定后才被允许使用；不得篡改信号 |
| **ENFSI 量表** | 似然比的言语类别映射 | 确定性查表；禁止统计再解释 |
| **from_raw()** | 从未经处理的整数或有理数观测值构建 `SignalOutput` | 通过确定性整数运算计算标准化指数 |
| **from_z_score()** | 将已预先计算的标准化指数封装进契约 | 跳过重复计算；保留输入值的精确形态 |
| **Pydantic / dataclass** | 后端验证技术 | 无论后端是否可用，模式强制执行效果完全一致 |

### 术语表

- **SignalContract（信号契约）**：正式接口规范，定义取证工具必须以何种格式输出数据。
- **SignalOutput（信号输出）**：标准化的传输对象。可将其视为贴有标签、并附带预印制保管链表单的取证试管。
- **SignalBuilder（信号构建器）**：工厂类，负责在封存试管前检查工具输出的完整性与正确性。
- **LikelihoodEngine（似然引擎）**：VIGÍA 的概率推理核心。它只能识别 `SignalOutput`。
- **Daubert**：要求专家证言具备科学可靠性与相关性的法律标准。信号契约的破坏将导致无法符合该标准。
- **SDA / CLI / GCI / ACP**：VIGÍA 内部的取证子工具。各工具产生的原始测量值都必须被封装为 `SignalOutput`。
- **z-score（标准分数）**：一种确定性标准化指数，表示观测值与基线均值之间相差多少个整数标准差。
- **ENFSI 量表**：七级言语量表（例如"有限支持""中等强度支持"），由似然比经确定性映射得到。
- **证据层**：确定性、无 LLM 参与的层级，原始观测值在此被转化为信号。
- **报告层**：自然语言报告生成层级，严格位于数值推断完成之后。
- **逻辑断裂**：由不合规数据格式导致的保管链条中断。

### 【科学说明】
VIGÍA 借用**皮尔斯**（符号学）、**艾柯**（诠释代码）与**格赖斯**（合作原则）的术语，来描述取证工具如何将数字痕迹转化为结构化符号。这并非神秘主义。

请设想一枚实验室传感器：热电偶依据物理契约将热能转换为电压。电压读数不是主观意见，而是信号。`SignalOutput` 就是取证传感器的"电压读数"。皮尔斯解释了该读数为何能够代表另一事物（其背后的取证工件）；艾柯解释了契约编码如何使该读数对 LikelihoodEngine 而言可被解读；格赖斯解释了工具必须合作性地披露哪些信息，以免推断引擎受到误导。该契约消除了歧义，正如经过校准的传感器消除了实验测量中的猜测。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
