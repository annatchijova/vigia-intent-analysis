<!--
VIGIA Academic Documentation
Module: 5a035ab4
Batch ID: vigia-doc-0143-5a035ab4
Generated: 2026-05-20T14:56:47.875267+00:00
-->

---
doc_hash: 5a035ab4
module: unknown
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

# ENGLISH

## What Is This Module?
This module is the chronological assembly line of the VIGIA forensic system. It collects observations from five distinct evidence domains—Network traffic, Disk storage, Memory (RAM), System Registry, and Log files—and merges them into one continuous, contradiction-free timeline. Think of it as a laboratory instrument that synchronizes clocks from five separate experiments so that causality can be determined with certainty. Every numeric value inside the evidence dictionary is stored as an exact rational number (integer numerator/denominator or its string representation); approximate decimal arithmetic is never used.

## Key Concepts

| Name | Role | Scientific Meaning |
|---|---|---|
| `TOOL_NAME` | Identifier | Name tag for the engine in audit reports. |
| `ARTIFACT_RELIABILITY` | Weight matrix | Confidence score assigned to each source type; a higher weight indicates a more trustworthy sensor. |
| `TEMPORAL_CORRELATION_WINDOW` | Tolerance threshold | Maximum allowable time gap between events before they are flagged as mismatched; expressed as an exact integer rational value. |

| Class | Purpose | Deterministic Guarantee |
|---|---|---|
| `TimelineEvent` | Atomic unit of time | Timestamp stored as a rational integer pair (`Fraction` / `str`); no rounding occurs. |
| `TimelineAnalysisResult` | Anomaly container | All temporal deltas are computed via exact integer-based arithmetic. |
| `UnifiedTimelineEngine` | Integration controller | Builds the unified timeline using deterministic integer arithmetic exclusively. |

| Function | Input | Output | Role |
|---|---|---|---|
| `to_signal()` | Raw forensic artifact | Normalized `TimelineEvent` | Translates heterogeneous source data into a common temporal language. |
| `build_timeline()` | Set of `TimelineEvent` objects | `TimelineAnalysisResult` | Correlates cross-source events and flags temporal paradoxes. |

## Glossary
- **Artifact**: Any digital object carrying evidentiary value (e.g., a file, network packet, or registry key).
- **Cross-source inconsistency**: A temporal paradox where two reliable sources disagree on when an action occurred.
- **Deterministic integer arithmetic**: Exact calculation using whole numbers and rational fractions (e.g., 1/2 represented as numerator/denominator), never approximate decimals.
- **Temporal correlation window**: The maximum acceptable clock skew between two events before the system registers a contradiction.
- **Signal**: A normalized observation that is ready for insertion into the timeline.

## 【Scientific Note】Peirce, Eco, and Grice in Digital Forensics
The terminology of semiotics—Charles Sanders Peirce’s sign-object-interpretant triad, Umberto Eco’s coding theory, and H. Paul Grice’s conversational maxims—is sometimes mistaken for philosophical mysticism. It is not. In this framework, forensic artifacts function as **semiotic sensors**.

- **Peirce’s triad**: A forensic artifact (sign) points to a past system state (object); the investigator’s inference (interpretant) reconstructs that state. This is identical to a thermometer reading (sign) representing temperature (object) interpreted by a scientist (interpretant).
- **Eco’s codes**: The encoding rules that govern how a log file formats time are no different from the calibration protocol of a spectrometer. They are deterministic conventions, not esoteric signs.
- **Grice’s maxims**: The assumption that a log timestamp is truthful and relevant is the same as assuming a voltmeter is properly grounded. Violations (temporal inconsistencies) are **sensor malfunctions or calibration drift**, not mystical paradoxes.

Treating these concepts as signal-processing parameters allows the engine to detect logical fractures in evidence through rigorous, deterministic arithmetic.

---

# ESPAÑOL

## ¿Qué es este módulo?
Es la línea de montaje cronológica del sistema forense VIGIA. Recoge observaciones de cinco dominios de evidencia distintos—tráfico de Red, almacenamiento en Disco, Memoria RAM, Registro del sistema y archivos de Logs—y los fusiona en una única línea temporal continua y libre de contradicciones. Considérelo como un instrumento de laboratorio que sincroniza relojes de cinco experimentos separados para que la causalidad pueda determinarse con certeza. Todo valor numérico en el diccionario de evidencia se almacena como un número racional exacto (numerador/denominador enteros o su representación textual); nunca se utiliza aritmética decimal aproximada.

## Conceptos Clave

| Nombre | Función | Significado Científico |
|---|---|---|
| `TOOL_NAME` | Identificador | Etiqueta del motor en informes de auditoría. |
| `ARTIFACT_RELIABILITY` | Matriz de pesos | Puntaje de confianza por tipo de fuente; mayor peso = sensor más fiable. |
| `TEMPORAL_CORRELATION_WINDOW` | Umbral de tolerancia | Brecha temporal máxima permitida antes de considerar dos eventos como incompatibles; expresado como racional entero exacto. |

| Clase | Propósito | Garantía Determinista |
|---|---|---|
| `TimelineEvent` | Unidad atómica de tiempo | Marca temporal almacenada como par de enteros (`Fraction` / `str`); sin redondeo. |
| `TimelineAnalysisResult` | Contenedor de anomalías | Todas las diferencias computadas mediante aritmética exacta. |
| `UnifiedTimelineEngine` | Controlador de integración | Construye la línea temporal usando únicamente aritmética entera determinista. |

| Función | Entrada | Salida | Rol |
|---|---|---|---|
| `to_signal()` | Artefacto forense en bruto | `TimelineEvent` normalizado | Traduce datos heterogéneos a un lenguaje temporal común. |
| `build_timeline()` | Conjunto de objetos `TimelineEvent` | `TimelineAnalysisResult` | Correlaciona eventos cross-source y señala paradojas temporales. |

## Glosario
- **Artefacto**: Cualquier objeto digital con valor probatorio (archivo, paquete, clave de registro, etc.).
- **Inconsistencia cross-source**: Paradoja temporal donde dos sensores fiables discrepan sobre cuándo ocurrió una acción.
- **Aritmética entera determinista**: Cálculo exacto con números enteros y fracciones racionales (p. ej., 1/2 como numerador/denominador), nunca decimales aproximados.
- **Ventana de correlación temporal**: Máxima desviación de reloj aceptable entre dos eventos antes de que el sistema marque una contradicción.
- **Señal**: En este contexto, una observación normalizada lista para inserción en la línea temporal.

## 【Nota Científica】Peirce, Eco y Grice en Informática Forense
La terminología de la semiótica—el triada signo-objeto-interpretante de Charles Sanders Peirce, la teoría de los códigos de Umberto Eco y las máximas conversacionales de H. Paul Grice—a veces se confunde con misticismo filosófico. No lo es. En este marco, los artefactos forenses funcionan como **sensores semióticos**.

- **Tríada de Peirce**: Un artefacto forense (signo) apunta a un estado pasado del sistema (objeto); la inferencia del investigador (interpretante) reconstruye ese estado. Es idéntico a la lectura de un termómetro (signo) que representa temperatura (objeto) e interpretada por un científico (interpretante).
- **Códigos de Eco**: Las reglas de codificación que gobiernan cómo un archivo de log formatea el tiempo no difieren del protocolo de calibración de un espectrómetro. Son convenciones deterministas, no signos esotéricos.
- **Máximas de Grice**: La suposición de que una marca temporal es veraz y relevante equivale a asumir que un voltímetro está correctamente conectado a tierra. Las violaciones (inconsistencias temporales) son **fallos de sensor o deriva de calibración**, no paradojas místicas.

Tratar estos conceptos como parámetros de procesamiento de señales permite al motor detectar fracturas lógicas en la evidencia mediante aritmética rigurosa y determinista.

---

# РУССКИЙ

## Что представляет собой этот модуль?
Это хронологическая сборочная линия судебно-экспертной системы VIGIA. Модуль собирает наблюдения из пяти различных областей доказательств — сетевого трафика (Red), дисковых накопителей (Disco), оперативной памяти (Memoria), системного реестра (Registro) и журналов (Logs) — и объединяет их в единую непрерывную временну́ю шкалу, свободную от противоречий. Воспринимайте его как лабораторный прибор, синхронизирующий часы пяти отдельных экспериментов, чтобы причинно-следственные связи можно было установить с достоверностью. Каждое числовое значение в словаре доказательств хранится в виде точного рационального числа (числитель/знаменатель целые или их строковое представление); приближённая десятичная арифметика никогда не применяется.

## Ключевые концепции

| Имя | Роль | Научное значение |
|---|---|---|
| `TOOL_NAME` | Идентификатор | Имя механизма в аудиторских отчётах. |
| `ARTIFACT_RELIABILITY` | Весовая матрица | Оценка достоверности по типу источника; больший вес = более надёжный датчик. |
| `TEMPORAL_CORRELATION_WINDOW` | Порог допуска | Максимально допустимый временной разрыв между событиями, прежде чем они будут признаны несовпадающими; выражен точным целым рациональным числом. |

| Класс | Назначение | Детерминистская гарантия |
|---|---|---|
| `TimelineEvent` | Атомарная единица времени | Отметка времени хранится как пара целых чисел (`Fraction` / `str`); округление отсутствует. |
| `TimelineAnalysisResult` | Контейнер аномалий | Все дельты вычисляются точной целочисленной арифметикой. |
| `UnifiedTimelineEngine` | Контроллер интеграции | Построение шкалы только с помощью детерминистской целочисленной арифметики. |

| Функция | Вход | Выход | Роль |
|---|---|---|---|
| `to_signal()` | Сырые судебные артефакты | Нормализованный `TimelineEvent` | Преобразует гетерогенные данные в общий временной язык. |
| `build_timeline()` | Набор объектов `TimelineEvent` | `TimelineAnalysisResult` | Коррелирует события из разных источников и маркирует временные парадоксы. |

## Глоссарий
- **Артефакт**: Любой цифровой объект, обладающий доказательственной ценностью (файл, пакет, ключ реестра и т.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
