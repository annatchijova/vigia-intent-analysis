<!--
VIGIA Academic Documentation
Module: 779b4236
Batch ID: vigia-doc-0026-779b4236
Generated: 2026-05-20T14:56:47.850241+00:00
-->

---

## ENGLISH

### What Is This Module?
`vigia_batch_doc_generator.py` is a deterministic document-preparation engine. It performs an inventory sweep of a digital repository, excludes irrelevant materials using exact-pattern filters, and fabricates standardized instruction sets (prompts) for batch artificial-intelligence analysis. Imagine a laboratory autosampler: it counts vials using whole numbers, rejects contaminated samples via exact rules, and loads reagents according to a fixed protocol. Every operation—file counting, line indexing, and catalog sorting—uses deterministic integer arithmetic, producing identical outputs on every run.

### Key Concepts

| Function / Constant | Plain-Language Role | Deterministic Mechanism |
|---|---|---|
| `scan_repo()` | Repository inventory sweep | Integer enumeration of files; exact string-match exclusion of skip patterns |
| `generate_md_prompts()` | Fabrication of Markdown instruction sets | Template substitution with fixed text scaffolds; no probabilistic variation |
| `generate_batch_jsonl()` | Containerization for external batch queue | One JSON record per line; sequential integer line numbers |
| `generate_master_index()` | Consolidated catalog generation | Alphabetical sorting; integer ID assignment |
| `main()` | Orchestration controller | Sequential execution pipeline with defined entry and exit states |
| `DEFAULT_REPO` | Root source path | Fixed filesystem pointer |
| `OUTPUT_DIR` / `BATCH_DIR` | Destination directories | Deterministic path strings |
| `SKIP_DIRS` / `SKIP_FILES` / `SKIP_PATTERNS` | Contamination filters | Exact-match string exclusion; no heuristic or fuzzy logic |
| `ACADEMIC_PROMPT_TEMPLATE` | Standard reagent formula | Fixed textual scaffold ensuring reproducible AI instructions |
| `SIMPLE_PROMPT_TEMPLATE` | Minimal reagent formula | Fixed textual scaffold for lightweight processing |

### Glossary

- **Batch API**: A queued remote-processing interface that accepts multiple analysis jobs in a single deterministic container.
- **Deterministic Integer Arithmetic**: Mathematical operations using whole numbers only (counting, indexing, ordering) that yield bit-for-bit identical results across every execution.
- **Forensic Artifact** (取证工件): Any file, log, or data object subjected to evidentiary examination.
- **JSONL**: JSON Lines format—one self-contained, deterministic record per line, terminated by a newline character.
- **Logical Fracture** (逻辑断裂): A discontinuity in code or narrative logic that breaks deterministic expectations and requires analyst review.
- **Prompt Template**: A pre-structured instruction frame that constrains an AI engine to reproducible behavior.
- **Repository**: A structured directory containing source code and associated materials.
- **Skip Pattern**: An exact string rule used to exclude irrelevant directories or files from processing.

### Scientific Note

> 【Scientific Note】The semiotic terminology of Peirce, Eco (艾柯), and Grice (格赖斯) employed within the VIGIA framework is not mysticism. Treat these constructs as **deterministic sensors**. Peirce’s trichotomy operates like a spectrometer that classifies signs into three discrete integer states (icon, index, symbol). Eco’s codes function as calibration matrices that map forensic artifacts onto exact interpretive protocols. Grice’s maxims serve as threshold filters that flag logical fractures whenever communication violates deterministic bounds. The system introduces no floating-point uncertainty; it relies upon integer-state classification, exact pattern matching, and reproducible cataloging—analogous to digital logic gates, not oracular divination.

---

## ESPAÑOL

### ¿Qué es este módulo?
`vigia_batch_doc_generator.py` es un motor determinista de preparación documental. Realiza un barrido de inventario de un repositorio digital, excluye materiales irrelevantes mediante filtros de patrón exacto y fabrica conjuntos de instrucciones estandarizadas (prompts) para análisis por lotes con inteligencia artificial. Imagínese un autosampler de laboratorio: cuenta viales con números enteros, rechaza muestras contaminadas mediante reglas exactas y carga reactivos según un protocolo fijo. Cada operación—conteo de archivos, indexación de líneas y ordenación de catálogos—utiliza aritmética entera determinista, produciendo resultados idénticos en cada ejecución.

### Conceptos clave

| Término / Constante | Función en lenguaje sencillo | Mecanismo determinista |
|---|---|---|
| `scan_repo()` | Barrido de inventario del repositorio | Enumeración entera de archivos; exclusión por coincidencia exacta de patrones de omisión |
| `generate_md_prompts()` | Fabricación de conjuntos de instrucciones Markdown | Sustitución en plantilla con andamios de texto fijos; sin variación probabilística |
| `generate_batch_jsonl()` | Contenerización para cola externa por lotes | Un registro JSON por línea; números de línea secuenciales enteros |
| `generate_master_index()` | Generación de catálogo consolidado | Ordenamiento alfabético; asignación de ID enteros |
| `main()` | Controlador de orquestación | Pipeline de ejecución secuencial con estados de entrada y salida definidos |
| `DEFAULT_REPO` | Ruta fuente raíz | Puntero fijo del sistema de archivos |
| `OUTPUT_DIR` / `BATCH_DIR` | Directorios de destino | Cadenas de ruta deterministas |
| `SKIP_DIRS` / `SKIP_FILES` / `SKIP_PATTERNS` | Filtros de contaminación | Exclusión por coincidencia exacta de cadenas; sin lógica heurística ni difusa |
| `ACADEMIC_PROMPT_TEMPLATE` | Fórmula de reactivo estándar | Andamio textual fijo que garantiza instrucciones reproducibles para IA |
| `SIMPLE_PROMPT_TEMPLATE` | Fórmula de reactivo mínima | Andamio textual fijo para procesamiento ligero |

### Glosario

- **API por lotes (Batch API)**: Interfaz de procesamiento remoto en cola que acepta múltiples trabajos de análisis en un solo contenedor determinista.
- **Aritmética entera determinista**: Operaciones matemáticas que usan solo números enteros (conteo, indexación, ordenación) y producen resultados idénticos bit a bit en cada ejecución.
- **Artefacto forense** (取证工件): Cualquier archivo, registro u objeto de datos sometido a examen probatorio.
- **JSONL**: Formato JSON Lines — un registro determinista y autocontenido por línea, terminado con carácter de nueva línea.
- **Fractura lógica** (逻辑断裂): Discontinuidad en la lógica de código o narrativa que rompe las expectativas deterministas y requiere revisión del analista.
- **Plantilla de prompt (Prompt Template)**: Marco de instrucción preestructurado que restringe el motor de IA a un comportamiento reproducible.
- **Repositorio**: Directorio estructurado que contiene código fuente y materiales asociados.
- **Patrón de omisión (Skip Pattern)**: Regla de cadena exacta para excluir directorios o archivos irrelevantes del procesamiento.

### Nota científica

> 【Scientific Note】La terminología semiótica de Peirce, Eco (艾柯) y Grice (格赖斯) empleada en el marco VIGIA no es mistica. Considere estos constructos como **sensores deterministas**: la tricotomía de Peirce opera como un espectrómetro que clasifica signos en tres estados enteros discretos (icono, índice, símbolo); los códigos de Eco funcionan como matrices de calibración que mapean artefactos forenses a protocolos interpretativos exactos; las máximas de Grice actúan como filtros de umbral que señalan fracturas lógicas cuando la comunicación viola límites deterministas. El sistema no introduce incertidumbre de punto flotante; se basa en clasificación por estados enteros, coincidencia exacta de patrones y catalogación reproducible — análogo a compuertas lógicas digitales, no a adivinación oracular.

---

## РУССКИЙ

### Что это
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

## 中文

### 这是什么模块？

`vigia_batch_doc_generator.py` 是一个确定性文档准备引擎。它对数字代码仓库执行清单扫描，通过精确模式过滤器排除无关材料，并为批量人工智能分析生成标准化指令集（提示词）。可将其理解为实验室自动进样器：用整数计数样品瓶，通过精确规则拒绝受污染样品，并按固定协议加载试剂。

每项操作——文件计数、行索引、目录排序——均使用确定性整数运算，在每次运行中产生相同的输出。所有排除规则（`SKIP_DIRS`、`SKIP_FILES`、`SKIP_PATTERNS`）均为精确字符串匹配，不含任何启发式或模糊逻辑。提示词模板（`ACADEMIC_PROMPT_TEMPLATE`、`SIMPLE_PROMPT_TEMPLATE`）为固定文本框架，确保 AI 引擎产生可重现行为。

本模块是 VIGÍA 取证文档生成基础设施的组成部分，其输出（JSONL 批次文件和主索引）可作为 VIGÍA 分析流水线中的确定性取证工件使用。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **`scan_repo()`** | 仓库清单扫描 | 文件整数枚举；通过精确字符串匹配排除跳过模式 |
| **`generate_md_prompts()`** | Markdown 指令集生成 | 使用固定文本框架进行模板替换；无概率性变化 |
| **`generate_batch_jsonl()`** | 外部批处理队列容器化 | 每行一条 JSON 记录；顺序整数行号 |
| **`generate_master_index()`** | 综合目录生成 | 按字母顺序排序；整数 ID 分配 |
| **`SKIP_PATTERNS`** | 污染过滤器 | 精确字符串排除；无启发式或模糊逻辑 |
| **提示词模板** | 标准试剂配方 | 固定文本框架，确保 AI 指令的可重现性 |
| **`main()`** | 编排控制器 | 具有定义进入和退出状态的顺序执行流水线 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性，不依赖浮点近似。取证工件链的逻辑断裂以整数标志事件的形式被检测，而非直觉判断。皮尔斯的三分法如同将符号分类为三种离散整数状态（图标、索引、符号）的光谱仪；艾柯的代码是将取证工件映射至精确解释协议的校准矩阵；格赖斯的准则是当传播违反确定性边界时标记逻辑断裂的阈值过滤器。

### 词汇表

1. **批处理 API** — 接受单个确定性容器中多个分析任务的队列远程处理接口。
2. **确定性整数运算** — 仅使用整数（计数、索引、排序）的数学操作，在每次执行中产生逐位一致的结果。
3. **取证工件** — 接受证据审查的任何文件、日志或数据对象。
4. **JSONL** — JSON Lines 格式——每行一条自包含的确定性记录，以换行符终止。
5. **逻辑断裂** — 代码或叙述逻辑中打破确定性预期并需要分析员审查的不连续性。
6. **提示词模板** — 将 AI 引擎约束为可重现行为的预结构化指令框架。
7. **跳过模式** — 用于从处理中排除无关目录或文件的精确字符串规则。
8. **仓库** — 包含源代码和相关材料的结构化目录。
9. **SHA-256 哈希链** — 将每个文档生成事件密码学绑定至先前事件的不可篡改日志机制。
10. **法证可重现性** — 对于相同仓库状态，在任意执行环境中产生相同批次输出的属性。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
