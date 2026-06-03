<!--
VIGIA Academic Documentation
Module: e21ddd66
Batch ID: vigia-doc-0156-e21ddd66
Generated: 2026-05-20T14:56:47.878155+00:00
-->

---

## ENGLISH

### What Is This Module?

...

### Key Concepts

...

### Glossary

...

### 【Scientific Note】

...

---

## ESPAÑOL

### ¿Qué es este módulo?

...

### Conceptos clave

...

### Glosario

...

### 【Nota Científica】

...

---

## РУССКИЙ

### Что представляет собой этот модуль?

...

### Ключевые концепции

...

### Глоссарий

...

### 【Научное примечание】

...

---

## 中文

### 本模块是什么？

...

### 核心概念

...

### 术语表

...

### 【科学说明】

...

```

Let's double check the content for floating-point explanations. I must not explain floating point math. I can mention that the engine avoids floating-point approximations by using integer epoch seconds and deterministic median operations. I should not explain how floats work or why they are bad beyond stating the system is free from their uncertainty.

In the English glossary, I used "without floating-point approximations in the primary pipeline." That's okay; it's not explaining floating-point math, just stating the absence.

Now, ensure the term "Peirce/Eco/Grice" appears in the scientific note. Yes.

Let's verify the Spanish scientific note uses "Peirce, Eco y Grice". Yes.

Russian: "Пирса, Эко и Грайса". Yes.

Chinese: "皮尔斯、艾柯与格赖斯". Yes.

Now, check the Chinese required terms:
- 艾柯: present.
- 格赖斯: present.
- 取证工件: I will add to glossary.
- 逻辑断裂: I will add to glossary.

Add Chinese glossary entries:
- 取证工件: 由引擎生成的、用于法务或科学审查的不可变数据对象。本模块输出的 SignalOutput 即属此类。
- 逻辑断裂: 证据符号结构中的不连续性，常指示合成来源；GCI 通过确定性整数运算检测此类断裂的时间维度表现。

Now, ensure I mention deterministic integer arithmetic prominently.

Let's write the content fully.

**ENGLISH details:**

What Is This Module?
The file `vigia/tools/eml_gci.py` contains the **GCI Engine** (Generative Content Indicator). It is a forensic analysis module that examines sequences of time gaps—called *deltas*—between digital events (e.g., when a log entry was written, a document created, or an email edited). Its purpose is to reveal whether these intervals exhibit the mechanical regularity typical of automated generation, as opposed to the irregular rhythm of human activity. Crucially, the engine never discards information by returning a simple True/False flag. Instead, it returns a full numerical distribution (a z-score relative to an AUTHENTIC human baseline), allowing downstream systems to make informed, evidence-based decisions.

Key Concepts:
Table 1: Core Procedures
| Procedure | Scientific Role |
|---|---|
| `analyze_gci()` | Main entry point for the system bridge. Accepts either raw timestamps or pre-computed integer deltas. |
| `analyze_timestamps()` | Wrapper that converts epoch-second timestamps into integer deltas and delegates to the core analyzer. |
| `analyze_deltas()` | Core computation. Receives a list of whole-second intervals and deterministically computes the median absolute deviation (MAD) and the associated z-score against the baseline. |
| `build_baseline()` | Constructs the AUTHENTIC profile from collections of verified, human-generated delta sets. |
| `is_algorithmic()` | Derived advisory indicator only. It is a secondary interpretation of the z-score; the primary output remains the distribution itself. |
| `to_dict()` | Serializes the exact numeric results into a standardized dictionary structure. |
| `to_dict_display()` | Produces a rounded, human-readable view while preserving the exact underlying integers. |

Table 2: Classes & Configuration
| Name | Description |
|---|---|
| `GCIEngine` | Orchestrator that loads the baseline and executes deterministic comparisons on integer interval sets. |
| `GCIResult` | Enriched result container that always includes the full distribution, never a stripped boolean. |
| `_DEFAULT_ENGINE` | Singleton instance using the factory default baseline. |
| `MAX_INPUT_SIZE` | Upper limit on input cardinality to guarantee deterministic execution time and memory bounds. |

Glossary:
- **Delta**: The integer count of seconds between two consecutive events. The engine operates exclusively on these whole-number inputs.
- **Epoch second**: An integer timestamp counting seconds from the universal reference date 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: A robust statistic measuring spread via the median of absolute deviations from the median. It naturally suppresses the influence of outliers without discarding data.
- **z-score (in this module)**: A deterministic index expressing how far an observed set of intervals deviates from the AUTHENTIC baseline, measured in MAD units. The computation uses exact integer inputs and deterministic scaling.
- **AUTHENTIC Baseline**: A pre-calibrated reference model derived from empirically verified human-generated timestamps.
- **Trust Decay**: A fixed penalty coefficient (0.4) applied to a trust score when the z-score exceeds the threshold of 2, signaling strong algorithmic regularity.
- **Heavy-tailed distribution**: A probability distribution where extreme values occur more frequently than in a normal distribution, necessitating robust statistics like MAD.
- **Outlier**: An extreme observation that lies far from the central tendency of the dataset.
- **Deterministic integer arithmetic**: Exact calculations performed on integer inputs (seconds, counts, ranks) that yield reproducible results without reliance on floating-point approximations.

【Scientific Note】
Semiotic terminology invoked elsewhere in the VIGIA framework—deriving from Peirce, Eco, and Grice—is an analytical instrumentation suite, not mysticism. Treat these terms as sensors: a spectrometer does not “believe” in light; it registers specific wavelengths. Likewise, these conceptual sensors register classes of logical relations within evidence. The GCI Engine itself is built upon deterministic integer arithmetic: exact counts of epoch seconds and exact median deviations. This design guarantees that every measurement is reproducible and free from the uncertainty introduced by floating-point representations.

**ESPAÑOL details:**

¿Qué es este módulo?
El archivo `vigia/tools/eml_gci.py` alberga el **Motor GCI** (Generative Content Indicator). Es un módulo de análisis forense que examina secuencias de intervalos temporales —llamados *deltas*— entre eventos digitales (por ejemplo, la escritura de una entrada de registro, la creación de un documento o la edición de un correo). Su finalidad es revelar si dichos intervalos exhiben la regularidad mecánica propia de la generación automatizada, en contraste con el ritmo irregular de la actividad humana. Es crucial que el motor nunca descarte información devolviendo un simple flag Verdadero/Falso. En su lugar, retorna una distribución numérica completa (un z-score respecto a una línea base AUTHENTIC humana), permitiendo que los sistemas posteriores tomen decisiones informadas basadas en evidencia.

Conceptos clave:
Tabla 1: Procedimientos principales
| Procedimiento | Rol científico |
|---|---|
| `analyze_gci()` | Punto de entrada principal para el puente del sistema. Acepta timestamps o deltas enteros precomputados. |
| `analyze_timestamps()` | Envoltorio que convierte timestamps en segundos-epoch a deltas enteros y delega al analizador central. |
| `analyze_deltas()` | Cálculo central. Recibe una lista de intervalos en segundos enteros y computa de forma determinista la desviación absoluta mediana (MAD) y el z-score asociado contra la línea base. |
| `build_baseline()` | Construye el perfil AUTHENTIC a partir de colecciones de conjuntos de deltas verificados de origen humano. |
| `is_algorithmic()` | Indicador derivado meramente informativo. Es una interpretación secundaria del z-score; la salida primaria sigue siendo la distribución. |
| `to_dict()` | Serializa los resultados numéricos exactos en un diccionario estandarizado. |
| `to_dict_display()` | Produce una vista redondeada legible para humanos preservando los enteros exactos subyacentes. |

Tabla 2: Clases y configuración
| Nombre | Descripción |
|---|---|
| `GCIEngine` | Orquestador que carga la línea base y ejecuta comparaciones deterministas sobre conjuntos de intervalos enteros. |
| `GCIResult` | Contenedor de resultado enriquecido que siempre incluye la distribución completa, nunca un booleano reducido. |
| `_DEFAULT_ENGINE` | Instancia singleton que utiliza la línea base por defecto de fábrica. |
| `MAX_INPUT_SIZE` | Límite superior de cardinalidad de entrada para garantizar tiempos de ejecución y límites de memoria deterministas. |

Glosario:
- **Delta**: Recuento entero de segundos entre dos eventos consecutivos. El motor opera exclusivamente sobre estas entradas de números enteros.
- **Segundo epoch**: Marca temporal de número entero que cuenta segundos desde la fecha de referencia universal 1970-01-01 UTC.
- **MAD (Median Absolute Deviation)**: Estadístico robusto que mide la dispersión mediante la mediana de las desviaciones absolutas respecto a la mediana. Suprime naturalmente la influencia de valores atípicos sin descartar datos.
- **z-score (en este módulo)**: Índice determinista que expresa cuánto se desvía un conjunto observado de intervalos de la línea base AUTHENTIC, medido en unidades MAD. El cálculo utiliza entradas enteras exactas y escalamiento determinista.
- **Línea base AUTHENTIC**: Modelo de referencia precalibrado derivado de marcas temporales de origen humano verificadas empíricamente.
- **Trust Decay (Decaimiento de confianza)**: Coeficiente de penalización fijo (0,4) aplicado a una puntuación de confianza cuando el z-score supera el umbral de 2, señalando una regularidad algorítmica fuerte.
- **Distribución de colas pesadas (heavy-tailed)**: Distribución de probabilidad donde los valores extremos ocurren con mayor frecuencia que en una distribución normal, lo que hace necesario el uso de estadísticos robustos como MAD.
- **Valor atípico (outlier)**: Observación extrema que se sitúa lejos de la tendencia central del conjunto de datos.
- **Aritmética entera determinista**: Cálculos exactos realizados sobre entradas enteras (segundos, conteos, rangos) que producen resultados reproducibles sin recurrir a aproximaciones de coma flotante en la canalización principal.

【Nota Científica】
La terminología semiótica invocada en el marco VIGIA —derivada de Peirce, Eco y Grice— constituye un arsenal de instrumentación analítica, no misticismo. Considere estos términos como sensores: un espectrómetro no «cree» en la luz, sino que registra longitudes de onda específicas. De igual modo, estos sensores conceptuales registran clases de relaciones lógicas dentro de la evidencia. El Motor GCI se construye sobre aritmética entera determinista: conteos exactos de segundos-epoch y desviaciones medianas exactas. Este diseño garantiza que cada medición sea reproducible y libre de la incertidumbre introducida por las representaciones de coma flotante.

**РУССКИЙ details:**

Что представляет собой этот модуль?
Файл `vigia/tools/eml_gci.py` содержит **движок GCI** (Generative Content Indicator — Индикатор генеративного контента). Это судебно-аналитический модуль, исследующий последовательности временны́х промежутков — *дельт* — между цифровыми событиями (например, записью в журнале, созданием документа или редактированием электронной почты). Его цель — выявить, обнаруживают ли эти интервалы механическую регулярность, характерную для автоматической генерации, в отличие от нерегулярного ритма человеческой деятельности. Важно, что движок никогда не уничтожает информацию, возвращая простой флаг Истина/Ложь. Вместо этого он выдаёт полное числовое распределение (z-score относительно человеческой базы AUTHENTIC), позволяя последующим системам принимать обоснованные решения на основе доказательств.

Ключевые концепции:
Таблица 1. Основные процедуры
| Процедура | Научное назначение |
|---|---|
| `analyze_gci()` | Главная точка входа для системного моста. Принимает либо исходные временные метки, либо предварительно вычисленные целочисленные дельты. |
| `analyze_timestamps()` | Обертка, преобразующая временные метки в эпохальных секундах в целочисленные дельты с делегированием центральному анализатору. |
| `analyze_deltas()` | Центральное вычисление. Получает список интервалов в целых секундах и детерминированно вычисляет медианное абсолютное отклонение (MAD) и соответствующий z-score относительно базы. |
| `build_baseline()` | Строит профиль AUTHENTIC на основе собраний проверенных человеческих наборов дельт. |
| `is_algorithmic()` | Производный информационный индикатор. Это вторичная интерпретация z-score; первичным результатом остаётся само распределение. |
| `to_dict()` | Сериализует точные числовые результаты в стандартизированную структуру словаря. |
| `to_dict_display()` | Формирует округлённое, удобочитаемое представление, сохраняя при этом точные целочисленные данные в основе. |

Таблица 2. Классы и конфигурация
| Имя | Опис
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
