<!--
VIGIA Academic Documentation
Module: c8cb7042
Batch ID: vigia-doc-0121-c8cb7042
Generated: 2026-05-20T14:56:47.870660+00:00
-->

---

## ENGLISH

### What Is This Module?
This script is the digital equivalent of a controlled laboratory bench. It takes a collection of digital specimens (the dataset), runs each one through the VIGÍA analysis pipeline, and compares the machine’s judgment against a pre-established answer sheet known as the **ground truth**. Every decision is made with exact whole numbers—integers—so that the same dataset always yields exactly the same counts and classifications. The module produces three permanent records: a human-readable table (CSV), a summary of integer-derived metrics (JSON), and a complete case-by-case archive (JSON).

### Key Concepts

| Concept | Plain-Language Definition |
|---|---|
| **Ground Truth** | The pre-labeled answer sheet. Every specimen is marked **ADVERSARIAL** (hostile) or **BENIGN** (harmless) before testing begins. |
| **Alert Level** | The discrete label output by the detector for a given specimen. |
| **Detection Threshold** | A fixed integer boundary. If a specimen’s internal score is at or above this boundary, the detector issues an alert. |
| **Precision** | Of all specimens declared adversarial, how many were truly adversarial. Computed as an exact ratio of integer counts: TP ÷ (TP + FP). |
| **Recall** | Of all truly adversarial specimens, how many the detector caught. Computed as an exact ratio of integer counts: TP ÷ (TP + FN). |
| **FPR** (False Positive Rate) | Of all truly benign specimens, how many were wrongly declared adversarial. Computed as an exact ratio of integer counts: FP ÷ (FP + TN). |
| **Deterministic Integer Arithmetic** | Every comparison and count uses exact integers. There is no rounding, no decimal drift, and no floating-point uncertainty. Re-running the same data produces bit-identical results. |
| **CSV / JSON** | Archive formats. CSV is a table readable by spreadsheet software. JSON is a structured text file for automated data exchange. |

### Module Components

**Classes**
- **`GroundTruth`** — A sealed container that stores the known labels for every specimen. It enforces a strict two-word vocabulary: ADVERSARIAL or BENIGN.
- **`EvaluationResult`** — A sealed container that holds the outcome of one full evaluation run, including integer counts and file paths.

**Functions**
- **`run_pipeline()`** — Executes the complete VIGÍA analysis sequence on the dataset and normalizes the output to match the `compare_runs` schema (aggregate statistics plus normalized per-case records).
- **`evaluate()`** — The adjudicator. Compares each alert level against the ground truth and tabulates True Positives, False Positives, True Negatives, and False Negatives using only integer arithmetic.
- **`main()`** — The coordinator. Orchestrates the run, invokes evaluation, and exports the three output files.

**Constants**
- **`DETECTION_THRESHOLD`** — The immutable integer cutoff that separates a declared alert from a non-alert.
- **`LEVEL_ORDER`** — A fixed sequence that ranks alert severity from lowest to highest, ensuring that every comparison follows a single, unambiguous rule.

### Glossary

- **Pipeline** — A fixed assembly-line sequence of analysis steps applied uniformly to every specimen.
- **Schema** — A strict template defining which fields must appear in every record and in what form.
- **Normalization** — The process of forcing diverse outputs into one uniform shape so they can be compared directly.
- **True Positive (TP)** — An adversarial specimen correctly identified as adversarial.
- **False Positive (FP)** — A benign specimen incorrectly identified as adversarial.
- **True Negative (TN)** — A benign specimen correctly identified as benign.
- **False Negative (FN)** — An adversarial specimen incorrectly identified as benign.
- **Meta-metric** — A measurement of a measurement (for example, timing how long a stopwatch runs). This module reports direct evidentiary counts, not meta-metrics.

### 【Scientific Note】
VIGÍA employs terminology derived from semiotics (Charles Sanders Peirce, Umberto Eco) and linguistic pragmatics (H. Paul Grice) to formalize how meaning is extracted from forensic artifacts. This vocabulary is **not** mysticism or literary criticism. It functions exactly like a physical sensor protocol: a spectrometer does not “interpret” a sample through intuition; it applies calibrated physical rules to produce a deterministic signal. Similarly, Peirce’s *sign relation*, Eco’s *code*, and Grice’s *cooperative maxims* are deployed here as hard logical constraints. They act as deterministic filters on information flow, reducing ambiguity when a digital artifact is read. The terminology is a compact notation for boundary conditions in evidence processing, analogous to setting a threshold voltage on an analog-to-digital converter. The result is reproducible, measurable, and entirely independent of subjective belief.

---

## ESPAÑOL

### ¿Qué es este módulo?
Este script es el equivalente digital de un banco de laboratorio controlado. Toma una colección de especímenes digitales (el conjunto de datos), los procesa uno por uno a través del pipeline de análisis de VIGÍA y compara el veredicto de la máquina contra una hoja de respuestas preestablecida llamada **ground truth** (verdad de campo). Cada decisión se toma con números enteros exactos, de modo que el mismo conjunto de datos siempre produce exactamente los mismos conteos y clasificaciones. El módulo genera tres registros permanentes: una tabla legible por humanos (CSV), un resumen de métricas derivadas de enteros (JSON) y un archivo completo caso por caso (JSON).

### Conceptos clave

| Concepto | Definición en lenguaje sencillo |
|---|---|
| **Ground truth** | La hoja de respuestas previamente etiquetada. Cada espécimen se marca como **ADVERSARIAL** (hostil) o **BENIGN** (inofensivo) antes de iniciar la prueba. |
| **Alert level** | La etiqueta discreta que emite el detector para un espécimen dado. |
| **Detection threshold** | Un límite entero fijo. Si la puntuación interna del espécimen es igual o superior a este límite, el detector emite una alerta. |
| **Precision** (Precisión) | De todos los especímenes declarados adversariales, cuántos lo eran realmente. Se computa como una razón exacta de conteos enteros: VP ÷ (VP + FP). |
| **Recall** (Sensibilidad) | De todos los especímenes realmente adversariales, cuántos detectó el sistema. Se computa como una razón exacta de conteos enteros: VP ÷ (VP + FN). |
| **FPR** (Tasa de falsos positivos) | De todos los especímenes realmente benignos, cuántos fueron declarados erróneamente adversariales. Se computa como una razón exacta de conteos enteros: FP ÷ (FP + VN). |
| **Aritmética entera determinista** | Toda comparación y conteo usa enteros exactos. No hay redondeo, ni deriva decimal, ni incertidumbre de punto flotante. Reprocesar los mismos datos produce resultados idénticos bit a bit. |
| **CSV / JSON** | Formatos de archivo. CSV es una tabla que se puede abrir en una hoja de cálculo. JSON es un archivo de texto estructurado para intercambio automatizado. |

### Componentes del módulo

**Clases**
- **`GroundTruth`** — Un contenedor sellado que almacena las etiquetas conocidas de cada espécimen. Impone un vocabulario estricto de dos palabras: ADVERSARIAL o BENIGN.
- **`EvaluationResult`** — Un contenedor sellado que guarda el resultado de una evaluación completa, incluyendo conteos enteros y rutas de archivo.

**Funciones**
- **`run_pipeline()`** — Ejecuta la secuencia completa de análisis de VIGÍA sobre el conjunto de datos y normaliza la salida para que coincida con el esquema `compare_runs` (estadísticas agregadas más registros normalizados por caso).
- **`evaluate()`** — El juez. Compara cada nivel de alerta contra el *ground truth* y tabula Verdaderos Positivos, Falsos Positivos, Verdaderos Negativos y Falsos Negativos usando únicamente aritmética entera.
- **`main()`** — El coordinador. Orquesta la ejecución, invoca la evaluación y exporta los tres archivos de salida.

**Constantes**
- **`DETECTION_THRESHOLD`** — El punto de corte entero e inmutable que separa una alerta declarada de una no-alerta.
- **`LEVEL_ORDER`** — Una secuencia fija que ordena la severidad de las alertas de menor a mayor, garantizando que toda comparación siga una regla única e inequívoca.

### Glosario

- **Pipeline** — Una secuencia de pasos de análisis aplicados uniformemente a cada espécimen, como una línea de ensamblaje.
- **Schema** (Esquema) — Una plantilla estricta que define qué campos debe contener cada registro y en qué forma.
- **Normalization** (Normalización) — El proceso de forzar salidas diversas a una forma uniforme para poder compararlas directamente.
- **Verdadero Positivo (VP / TP)** — Un espécimen adversarial correctamente identificado como adversarial.
- **Falso Positivo (FP)** — Un espécimen benigno incorrectamente identificado como adversarial.
- **Verdadero Negativo (VN / TN)** — Un espécimen benigno correctamente identificado como benigno.
- **Falso Negativo (FN)** — Un espécimen adversarial incorrectamente identificado como benigno.
- **Meta-métrica** — Una medición de una medición (por ejemplo, cronometrar cuánto dura un temporizador). Este módulo reporta conteos directos de evidencia, no meta-métricas.

### 【Nota Científica】
VIGÍA utiliza terminología de la semiótica (Charles Sanders Peirce, Umberto Eco) y la pragmática lingüística (H. Paul Grice) para formalizar la extracción de significado a partir de artefactos forenses. Este vocabulario **no** es misticismo ni crítica literaria. Funciona exactamente como el protocolo de un sensor físico: un espectrómetro no “interpreta” una muestra por intuición, sino que aplica reglas físicas calibradas para producir una señal determinista. Así, la *relación significante* de Peirce, el *código* de Eco y las *máximas cooperativas* de Grice se despliegan aquí como restricciones lógicas estrictas. Actúan como filtros deterministas sobre el flujo de información, reduciendo la ambigüedad al leer un artefacto digital. La terminología es una notación compacta para condiciones de frontera en el procesamiento de evidencia, análoga a fijar un voltaje umbral en un conversor analógico-digital. El resultado es reproducible, medible e independiente de toda creencia subjetiva.

---

## РУССКИЙ

### Что представляет собой этот модуль?
Этот скрипт — цифровой аналог контролируемого лабораторного стенда. Он берёт коллекцию цифровых образцов (набор данных), пропускает каждый через аналитический конвейер VIGÍA и сравнивает вердикт системы с заранее подготовленным эталоном — **ground truth**. Каждое решение принимается с помощью точных целых чисел, так что один и тот же набор данных всегда даёт одинаковые подсчёты и классификации. Модуль создаёт три постоянных записи: таблицу для человека (CSV), сводку метрик, выведенных из целочисленных подсчётов (JSON), и полный архив по каждому случаю (JSON).

### Ключевые понятия

| Понятие | Определение простым языком |
|---|---|
| **Ground truth** (Эталонная разметка) | Заранее размеченный эталон. Каждый образец перед испытанием помечен как **ADVERSARIAL** (враждебный) или **BENIGN** (безвредный). |
| **Alert level** (Уровень тревоги) | Дискретная метка, которую детектор выдаёт для данного образца. |
| **Detection threshold** (Порог обнаружения) | Фиксированная целочисленная граница. Если внутренний счёт образца равен ей или выше, детектор объявляет тревогу. |
| **Precision** (Точность) | Сколько из всех объявленных враждебных образцов действительно враждебны. Вычисляется как точное отношение целочисленных подсчётов: TP ÷ (TP + FP). |
| **Recall** (Полнота) | Сколько из всех действительно враждебных образцов обнаружил детектор. Вычисляется как точное отношение целочисленных подсчётов: TP ÷ (TP + FN). |
| **FPR** (Частота ложных срабатываний) | Сколько из всех действительно безвредных образцов ошибочно объявлены враждебными. Вычисляется как точное отношение целочисленных подсчётов: FP ÷ (FP + TN). |
| **Детерминированная целочисленная арифметика** | Все сравнения и подсчёты используют точные целые числа. Никакого округления, десятичного дрейфа или неопределённости чисел с плавающей точкой. Повторный прогон тех же данных даёт бит-в-бит идентичный результат. |
| **CSV / JSON** | Форматы архивов. CSV — таблица, открываемая в электронных таблицах. JSON — структурированный текстовый файл для автоматизированного обмена данными. |

### Компоненты модуля

**Классы**
- **`GroundTruth`** — Запечатанный контейнер, хранящий известные метки каждого образца. Строго применяет словарь из двух слов: ADVERSARIAL или BENIGN.
- **`EvaluationResult`** — Запечатанный контейнер, хранящий результат полного цикла оценки, включая целочисленные подсчёты и пути к файлам.

**Функции**
- **`run_pipeline()`** — Выполняет полную последовательность анализа VIGÍA на наборе данных и нормализует вывод до схемы `compare_runs` (агрегированная статистика плюс нормализованные записи по каждому случаю).
- **`evaluate()`** — Судья. Сравнивает каждый уровень тревоги с эталонной разметкой и подсчитывает True Positives, False Positives, True Negatives и False Negatives, использ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*

## 中文

### 这是什么模块？

本脚本是受控实验室工作台的数字等价物。它接受一批数字样本（数据集），将每个样本逐一通过 VIGÍA 分析流水线，并将机器的判断与预先建立的**基准真值**（答案表）进行比对。每项决策均使用精确整数作出——因此相同数据集始终产生完全相同的计数和分类。

本模块生成三份永久记录：人类可读表格（CSV）、整数派生指标摘要（JSON）和逐案完整档案（JSON）。所有混淆矩阵条目（真阳性 TP、假阳性 FP、真阴性 TN、假阴性 FN）均以精确整数计数表示，精度（Precision）、召回率（Recall）和假阳性率（FPR）均以整数比率计算，不存在近似误差。

皮尔斯（Peirce）的符号关系、艾柯（Eco）的代码和格赖斯（Grice）的合作准则在此作为确定性过滤器用于信息流，在读取数字取证工件时减少歧义。术语是证据处理中边界条件的紧凑记号，类比模数转换器上设置阈值电压。

### 关键概念

| 概念 | 定义 | 技术作用 |
|---|---|---|
| **基准真值（Ground Truth）** | 预标记的答案表 | 每个样本在测试开始前标记为 ADVERSARIAL（敌对）或 BENIGN（良性） |
| **警报级别（Alert Level）** | 检测器为给定样本输出的离散标签 | 通过 `LEVEL_ORDER` 固定序列与 `DETECTION_THRESHOLD` 进行整数比较 |
| **检测阈值（Detection Threshold）** | 固定整数边界 | 样本内部评分达到或超过此边界时，检测器发出警报 |
| **精度（Precision）** | TP ÷ (TP + FP) | 以精确整数计数比率计算；无近似误差 |
| **召回率（Recall）** | TP ÷ (TP + FN) | 以精确整数计数比率计算；无近似误差 |
| **`evaluate()`** | 裁判函数 | 仅使用整数运算，将每个警报级别与基准真值比对并制表 |
| **确定性整数运算** | 所有比较和计数使用精确整数 | 无舍入、无小数漂移；重新处理相同数据产生逐位相同结果 |

> **【科学说明】**
> 皮尔斯（Peirce）、艾柯（Eco）和格赖斯（Grice）的术语并非神秘主义，而是形式化的分析机制。如同光谱仪将光子相互作用转换为离散整数计数，本模块将证据信号转换为确定性整数分数。精确整数运算确保法庭可重现性，不依赖浮点近似。取证工件链的逻辑断裂以整数标志事件的形式被检测，而非直觉判断。本模块将所有性能指标建立在整数计数基础上，等同于为模数转换器设置精确阈值电压：结果可重现、可测量，并完全独立于主观判断。

### 词汇表

1. **取证工件** — 通过 VIGÍA 分析流水线处理的任何数字样本；以 ADVERSARIAL 或 BENIGN 标记。
2. **基准真值** — 预先建立的已知标签，用于评估检测器性能。
3. **真阳性（TP）** — 被正确识别为敌对的敌对样本。
4. **假阳性（FP）** — 被错误识别为敌对的良性样本。
5. **真阴性（TN）** — 被正确识别为良性的良性样本。
6. **假阴性（FN）** — 被错误识别为良性的敌对样本。
7. **确定性整数运算** — 所有计数和比较使用精确整数，确保法庭可重现性。
8. **道伯特标准** — 要求科学证据可测试、具有已知误差率且经同行评审的美国联邦证据规则。
9. **规范化（Normalization）** — 将不同格式的输出强制为统一形式，使其可直接比较。
10. **法证可重现性** — 对于相同数据集，在任意执行环境中产生逐位相同评估结果的属性。

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
