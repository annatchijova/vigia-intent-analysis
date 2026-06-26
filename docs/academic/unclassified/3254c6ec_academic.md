<!--
VIGIA Academic Documentation
Module: 3254c6ec
Batch ID: vigia-doc-0029-3254c6ec
Generated: 2026-05-20T14:56:47.850876+00:00
-->

---

# ENGLISH

## What Is This Module?
This module is a deterministic scientific pipeline that transforms a digital evidence collection (`ForensicBundle`) into a directed topological map—a **Semantic Knowledge Graph of Artifacts**. Instead of treating a cyber intrusion as a simple timeline, the system models attacker behavior as a network of privilege expansion: processes, files, network connections, credentials, and log entries become nodes, while their causal or correlational relationships become directed edges. The resulting graph exposes lateral movement, choke points, and logical fractures within the victim infrastructure. The engine is built for reproducibility: all internal metrics are computed with integer arithmetic and lexicographically sorted traversals, eliminating bit-level variations between runs.

## Key Concepts

| Concept | Scientific Meaning | Role in Investigation |
|---|---|---|
| `ForensicBundle` | A normalized evidence container holding heterogeneous digital traces. | Input data source. |
| Semantic Knowledge Graph | A directed graph where vertices are forensic entities and edges are semantically meaningful relations. | Structural model of the incident. |
| Artifact Node | A single entity: process, file, credential, configuration key, log entry, or abductive hypothesis. | Atom of evidence. |
| Directed Edge | An asymmetric link indicating influence, flow, or derivation. | Causal or correlational pathway. |
| Lateral Movement | Adversary progression through a network via incremental privilege escalation. | Topological expansion pattern. |
| `FallbackGraph` | A redundant graph engine implemented in pure standard-library code, activated when NetworkX is absent. | Resilience guarantee. |
| Deterministic Output | Bit-for-bit reproducible results achieved via integer counts and sorted iteration order. | Scientific validity. |

## Glossary

- **Abductive Hypothesis** — An inference to the best explanation. A hypothesis node is generated when observed artifacts display a pattern best explained by a specific intrusion mechanism, analogous to a scientist proposing a theory from anomalous measurements.
- **Betweenness** — A topological measure of how frequently a node lies on the shortest path between other nodes, indicating control or brokerage points.
- **GEXF / GraphML / JSON** — Standard, platform-neutral exchange formats for graph data (compatible with Gephi, yEd, Cytoscape, and D3.js).
- **In-Degree / Out-Degree** — Integer counts of incoming and outgoing edges. High out-degree may identify a pivot point; high in-degree may indicate a data-collection target.
- **Lexicographic Sorting** — Alphanumeric ordering of identifiers to guarantee that every execution produces an identical sequence.
- **NetworkX** — An optional external library for advanced graph algorithms. The core system does not depend on it.
- **PageRank** — A linkage-topology centrality metric (when applicable) that ranks nodes by structural importance rather than chronology.
- **Privilege Expansion** — The spatial spread of access rights across a system, modeled as topological growth rather than temporal progression.

【Scientific Note】
Terms such as abduction (Peirce), semiotics (Eco), and conversational maxims (Grice) are formal epistemological instruments, not mysticism. Think of the system as a sensor array: when a physical sensor detects smoke, it does not "believe" in fire; it registers a deviation from baseline and infers a source via known physical laws. Similarly, an **abductive hypothesis** node is generated when the graph registers a **logical fracture**—a pattern break—that is best explained by a specific intrusion mechanism. Umberto Eco's semiotics provides a taxonomy for classifying signs (artifacts) by their relational function, while H.P. Grice's maxims describe expected cooperative behavior; violations of these maxims in log data become detectable anomalies. The graph does not perform divination. It applies rigorous inference rules to observable evidence, exactly as a spectrometer infers chemical composition from emission lines.

---

# ESPAÑOL

## ¿Qué es este módulo?
Este módulo es una tubería científica determinista que transforma una colección de evidencia digital (`ForensicBundle`) en un mapa topológico dirigido: un **Grafo de Conocimiento Semántico de Artefactos**. En lugar de ver una intrusión como una simple línea temporal, el sistema modela el comportamiento del atacante como una red de expansión de privilegios: procesos, archivos, conexiones de red, credenciales y entradas de registro se convierten en nodos, mientras que sus relaciones causales o correlacionales se convierten en aristas dirigidas. El grafo resultante revela patrones de movimiento lateral, puntos de estrangulamiento y fracturas lógicas en la infraestructura. El motor está diseñado para la reproducibilidad: todas las métricas internas se calculan con aritmética entera y recorridos ordenados lexicográficamente, eliminando variaciones a nivel de bit entre ejecuciones.

## Conceptos Clave

| Concepto | Significado Científico | Rol en la Investigación |
|---|---|---|
| `ForensicBundle` | Contenedor normalizado de evidencia que alberga trazos digitales heterogéneos. | Fuente de datos de entrada. |
| Grafo de Conocimiento Semántico | Grafo dirigido donde los vértices son entidades forenses y las aristas son relaciones semánticamente significativas. | Modelo estructural del incidente. |
| Nodo Artefacto | Una entidad única: proceso, archivo, credencial, clave de configuración,
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## РУССКИЙ

### Что это за модуль?
Данный модуль — детерминированный научный конвейер, преобразующий коллекцию цифровых улик (`ForensicBundle`) в направленную топологическую карту: **Семантический граф знаний об артефактах**. Вместо того чтобы рассматривать кибервторжение как простую хронологию, система моделирует поведение злоумышленника как сеть расширения привилегий: процессы, файлы, сетевые соединения, учётные данные и записи журналов становятся узлами, а их причинно-следственные или корреляционные отношения — направленными рёбрами. Полученный граф обнажает боковые перемещения, узкие места и логические разрывы в инфраструктуре жертвы.

Движок спроектирован для воспроизводимости: все внутренние метрики вычисляются через детерминированную целочисленную арифметику и лексикографически упорядоченные обходы, что устраняет побитовые вариации между запусками. Резервный граф (`FallbackGraph`) реализован в чистом стандартном библиотечном коде и активируется при отсутствии NetworkX, гарантируя устойчивость системы.

Каждый узел-гипотеза генерируется строго по детерминированному правилу: когда граф фиксирует логический разрыв — нарушение паттерна, — наиболее объясняемое конкретным механизмом вторжения. Это не интерпретация в человеческом смысле, а применение точных правил вывода к наблюдаемым доказательствам — именно так спектрометр выводит химический состав из спектральных линий.

### Ключевые концепции
| Концепция | Научный смысл | Роль в расследовании |
|---|---|---|
| ForensicBundle | Нормализованный контейнер улик, хранящий разнородные цифровые следы | Источник входных данных |
| Семантический граф знаний | Направленный граф, где вершины — форензические объекты, рёбра — семантически значимые отношения | Структурная модель инцидента |
| Узел-артефакт | Единственная сущность: процесс, файл, учётные данные, запись журнала или абдуктивная гипотеза | Атом доказательства |
| Направленное ребро | Асимметричная связь, указывающая влияние, поток или происхождение | Причинно-следственный или корреляционный путь |
| Боковое перемещение | Продвижение противника по сети через постепенное повышение привилегий | Паттерн топологического расширения |
| FallbackGraph | Резервный граф-движок на стандартной библиотеке, активируемый при отсутствии NetworkX | Гарантия устойчивости |
| Детерминированный вывод | Побитово воспроизводимые результаты через целочисленные счётчики и упорядоченный обход | Научная валидность |

> **【Научное примечание】**
> Терминология Пирса, Эко и Грайса — это не мистика, а формальная аналитическая механика. Как спектрометр преобразует фотонные взаимодействия в дискретные целочисленные отсчёты, этот модуль преобразует сигналы улик в детерминированные целочисленные оценки. Целочисленная арифметика гарантирует воспроизводимость в суде без округлений и аппроксимаций. Любое нарушение логики в цепочке артефактов фиксируется как целочисленный флаг, а не интуитивное суждение.

### Глоссарий
1. **Абдуктивная гипотеза** — Вывод к наилучшему объяснению: узел-гипотеза генерируется, когда наблюдаемые артефакты демонстрируют паттерн, наилучше объясняемый конкретным механизмом вторжения.
2. **Центральность по посредничеству** — Топологическая мера частоты, с которой узел лежит на кратчайшем пути между другими узлами, указывая на точки контроля.
3. **GEXF / GraphML / JSON** — Стандартные платформенно-нейтральные форматы обмена данными графов.
4. **Входящая / исходящая степень** — Целочисленное количество входящих и исходящих рёбер.
5. **Лексикографическая сортировка** — Буквенно-цифровое упорядочение идентификаторов для гарантии идентичности последовательности при каждом выполнении.
6. **NetworkX** — Необязательная внешняя библиотека для продвинутых алгоритмов графов; ядро системы от неё не зависит.
7. **PageRank** — Метрика центральности топологии связей, ранжирующая узлы по структурной важности.
8. **Расширение привилегий** — Пространственное распространение прав доступа по системе, моделируемое как топологический рост.
9. **Логический разрыв** — Нарушение ожидаемого паттерна в потоке улик, зафиксированное целочисленным флагом.
10. **ForensicBundle** — Нормализованный контейнер улик, хранящий разнородные цифровые следы.

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

---

## 中文

### 这是什么模块？
本模块是一个确定性科学流程，将数字证据集合（`ForensicBundle`）转换为有向拓扑图——**取证工件语义知识图谱**。系统不将网络入侵视为简单的时间线，而是将攻击者行为建模为权限扩张网络：进程、文件、网络连接、凭据和日志条目成为节点，其因果或相关关系成为有向边。生成的图谱揭示横向移动、瓶颈节点和受害者基础设施中的逻辑断裂。

该引擎为可重现性而构建：所有内部指标通过精确整数运算和字典序排序遍历计算，消除运行间的位级变化。备用图（`FallbackGraph`）以纯标准库代码实现，在NetworkX不可用时激活，保证系统鲁棒性。

每个假设节点严格按确定性规则生成：当图谱记录到逻辑断裂——一种最能由特定入侵机制解释的模式中断时触发。这不是人意义上的诠释，而是对可观察证据应用精确推理规则——如同光谱仪从谱线推断化学成分。

### 关键概念
| 概念 | 科学含义 | 在调查中的作用 |
|---|---|---|
| ForensicBundle | 存储异构数字痕迹的标准化证据容器 | 输入数据来源 |
| 语义知识图谱 | 顶点为取证实体、边为语义关系的有向图 | 事件的结构模型 |
| 工件节点 | 单一实体：进程、文件、凭据、日志条目或溯因假设 | 证据原子 |
| 有向边 | 表示影响、流动或推导的非对称链接 | 因果或相关路径 |
| 横向移动 | 攻击者通过逐步权限升级在网络中的推进 | 拓扑扩张模式 |
| FallbackGraph | 纯标准库实现的冗余图引擎，NetworkX不可用时激活 | 鲁棒性保证 |
| 确定性输出 | 通过整数计数和排序迭代顺序实现的逐位可重现结果 | 科学有效性 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性。取证工件链的逻辑断裂以整数标志事件形式被检测。

### 词汇表
1. **溯因假设** — 最佳解释推理：当观察到的取证工件显示出最能由特定入侵机制解释的模式时生成假设节点。
2. **介数中心性** — 节点位于其他节点最短路径上的频率的拓扑度量，指示控制或中介节点。
3. **GEXF / GraphML / JSON** — 图数据的标准、平台无关交换格式。
4. **入度/出度** — 入射和出射边的整数计数。
5. **字典序排序** — 标识符的字母数字排序，保证每次执行产生相同序列。
6. **NetworkX** — 高级图算法的可选外部库；核心系统不依赖它。
7. **PageRank** — 按结构重要性而非时序对节点排名的链接拓扑中心性度量。
8. **权限扩张** — 系统访问权限的空间传播，建模为拓扑增长而非时序进展。
9. **逻辑断裂** — 证据流中预期模式的中断，以整数标志记录。
10. **ForensicBundle** — 存储异构数字痕迹的标准化证据容器。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
