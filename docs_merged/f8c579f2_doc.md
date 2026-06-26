<!--
VIGIA Academic Documentation
Module: f8c579f2
Batch ID: vigia-doc-0169-f8c579f2
Generated: 2026-05-20T14:56:47.881203+00:00
-->

ENGLISH:
- What Is This Module?: This document describes the forensic mapping module `vigia/tools/picerl_mapping.py`. It translates digital artifacts from Incident Response (IR) phases into structured attacker-intent hypotheses within the PICERL-I (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned — Intent) framework. It replaces opaque guessing with deterministic lookup tables and mandatory falsifiability fields, ensuring every conclusion can be audited, reproduced, and challenged in a court of law under the Daubert standard.
- Key Concepts:
  - IRPhase: Enumerated stages of incident response.
  - PICERLPhase: Stages of the SANS PICERL lifecycle.
  - IntentHypothesis: A formal statement about attacker intent. Contains: intent_type (string), consistency_score (integer 0–100), what_would_falsify (string), source_artifact (string). No floating-point numbers are used; the score is an integer derived from deterministic table lookups.
  - PICERLMapper: The engine that maps IRPhase → PICERLPhase using only constant tables.
  - Constants: RECONNAISSANCE, etc. These are symbolic labels drawn from MITRE ATT&CK tactics, used as keys in the mapping tables.

Tables:
1. IntentHypothesis structure:
| Field | Type | Range / Constraint | Purpose |
|-------|------|--------------------|---------|
| intent_type | text | e.g., "RECONNAISSANCE" | Classifies attacker tactic |
| consistency_score | integer | 0–100 | Deterministic strength of hypothesis (no decimals) |
| what_would_falsify | text | non-empty string | Mandatory Daubert falsifiability criterion |
| source_artifact | text | file hash, log ID, etc. | 取证工件 (forensic artifact) provenance |

2. Mapping Logic (IRPhase → PICERLPhase):
| IR Phase | PICERL Phase | Rationale (example) |
|----------|--------------|---------------------|
| FOCUS_ANALYSIS (example) | IDENTIFICATION | Analyzed focal artifacts indicate ongoing intrusion |

The module seems to map IR phases to PICERL phases and also to IntentHypothesis (which includes an intent_type like RECONNAISSANCE, etc.). The constants are the intent types or PICERL subcategories. I'll present them as auditable symbolic constants used in the mapping tables.

Function table:
| Function | Input | Output | Method |
|----------|-------|--------|--------|
| map_focus_analysis_to_intent | IRPhase (e.g., FOCUS_ANALYSIS) | IntentHypothesis | Deterministic table lookup (P0-3) |
| map_abductive_result | AbductiveResult (from Ockham engine) | IntentHypothesis | Table-driven translation |
| generate_picerl_i_report | List[IntentHypothesis] | Human-readable report | Formatted serialization |
| to_dict | IntentHypothesis | Dictionary / Record | Lossless integer export |

Glossary:
- **AbductiveResult**: The output of an Ockham-prioritized inference engine that selects the simplest explanation for observed 取证工件.
- **Consistency Score**: An integer between 0 and 100 measuring how well a hypothesis coheres with known facts. Because it uses integer arithmetic, it is deterministic and free of rounding errors.
- **Daubert Standard**: A legal threshold requiring forensic methods to be testable, peer-reviewed, and subject to known error rates. This module satisfies it via 100% auditable tables and falsifiable hypotheses.
- **Deterministic Integer Arithmetic**: Calculations performed exclusively with whole numbers, guaranteeing that identical inputs always yield identical outputs.
- **Falsifiable Hypothesis**: A scientific claim paired with a concrete observation that could disprove it (the `what_would_falsify` field).
- **IR Phase**: A discrete stage in the Incident Response lifecycle (e.g., detection, analysis, containment).
- **PICERL**: The SANS six-phase incident response cycle: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. PICERL-I extends this with an explicit Intent layer.
- **PICERLMapper**: The rule engine that translates IR phases into PICERL-I phases using only constant lookup tables—no hidden conditional logic.
- **Peircean Abduction**: A logical inference form (C. S. Peirce) that generates the best available hypothesis from observed effects; implemented here as a deterministic table, not intuition.
- **Eco Semiotics**: Umberto Eco’s framework for interpreting signs; in this module, “signs” are 取证工件 whose meaning is fixed by explicit mapping tables.
- **Gricean Implicature**: Paul Grice’s theory of implied meaning derived from context; here, attacker intent is implied by artifact patterns only through auditable, explicit rules, never by subjective reading.

Scientific Note (EN):
> 【Scientific Note】
> The terminology of Peirce, Eco, and Grice is sometimes mistaken for literary theory or mysticism. In this forensic module, these concepts function exactly like physical sensors.
> - **Peircean abduction** is an alarm sensor: when a door opens (effect), the simplest explanation is “someone entered” (hypothesis). The module does not guess; it applies a deterministic lookup table that Peirce formalized logically.
> - **Eco’s semiotics** is a label sensor: a high temperature reading is a “sign” of fire only because we have an explicit convention (table) linking the signifier to the signified. The module uses explicit tables to link 取证工件 to intent categories, eliminating subjective interpretation.
> - **Gricean implicature** is a pattern-matching sensor: if a speaker says “it is cold” and the window is open, the implied meaning “close the window” is derived from context rules. The module derives attacker intent from contextual artifact patterns using only public, auditable rules.
> There is no mysticism. Every inference is a deterministic integer operation on explicitly defined tables.

ESPAÑOL:
- ¿Qué es este módulo?
- Tabla de conceptos clave.
- Glosario.
- Nota científica.

Need to adapt terms:
- Peirce, Eco, Grice.
- Puntuación de consistencia (consistency_score) entero.
- Aritmética entera determinista.
- Artefacto forense (but Chinese has specific term, Spanish can use "artefacto forense" or "artefacto de prueba").
- Lógica condicional oculta.

РУССКИЙ:
- Что представляет собой этот модуль?
- Таблицы.
- Глоссарий.
- Научное примечание.

Chinese:
- 本模块是什么？
- 关键概念表格。
- 术语表。
- 【科学说明】。


Also, do NOT use floating-point math explanations. Emphasize deterministic integer arithmetic. So when explaining consistency_score, say it's integer 0-100, no decimals, no rounding, fully reproducible.

Let's draft the content more carefully.

**ENGLISH**

# Module Documentation: `vigia/tools/picerl_mapping.py`

## What Is This Module?
This module is the deterministic translation engine of the VIGIA forensic suite. It converts observations from Incident Response (IR) phases into formal hypotheses about attacker intent, structured under the PICERL-I framework. Rather than relying on opaque code or human intuition, the module uses open, constant lookup tables and mandatory falsifiability fields. Every output is reproducible: the same digital evidence always produces the same integer consistency score and the same hypothesis classification. This design directly supports the Daubert standard for scientific evidence in legal proceedings.

### Key Concepts

**Table 1. Core Data Structure: `IntentHypothesis`**
| Field | Data Category | Constraint | Scientific Purpose |
|-------|---------------|------------|--------------------|
| `intent_type` | Symbolic label | One of the module constants (e.g., `RECONNAISSANCE`) | Classifies the tactical goal of the intruder |
| `consistency_score` | Integer | 0 to 100, inclusive | Deterministic measure of evidential support; computed without floating-point operations |
| `what_would_falsify` | Text | Non-empty string required | Satisfies the Daubert falsifiability requirement by stating exactly which evidence would disprove the hypothesis |
| `source_artifact` | Identifier | Hash, log serial, or file path | Provenance of the forensic artifact that triggered the hypothesis |

**Table 2. Mapping Philosophy: From IR to PICERL-I**
| Input (IR Phase) | Output (PICERL-I Phase) | Mechanism |
|------------------|-------------------------|-----------|
| Detection & Focus Analysis | IDENTIFICATION | Deterministic table lookup (`PICERLMapper`) |
| Abductive inference result (Ockham engine) | INTENT HYPOTHESIS | Table-driven translation (`map_abductive_result`) |

**Table 3. Auditable Module Constants (Partial List)**
| Constant | Denotation |
|----------|------------|
| `RECONNAISSANCE` | Pre-attack information gathering |
| `INITIAL_ACCESS` | First entry vector into the target system |
| `EXECUTION` | Running malicious code |
| `PERSISTENCE` | Maintaining access across reboots |
| `PRIVILEGE_ESCALATION` | Obtaining higher-level permissions |
| `DEFENSE_EVASION` | Avoiding detection tools |
| `CREDENTIAL_ACCESS` | Stealing passwords or tokens |
| `DISCOVERY` | Post-compromise network mapping |
| `LATERAL_MOVEMENT` | Moving between hosts |
| `COLLECTION` | Aggregating data for exfiltration |

**Table 4. Public Functions**
| Function | Input | Output | Guarantee |
|----------|-------|--------|-----------|
| `map_focus_analysis_to_intent()` | `IRPhase` enumeration | `IntentHypothesis` | Uses only lookup tables; no hidden conditionals (P0-3) |
| `map_abductive_result()` | `AbductiveResult` (Ockham) | `IntentHypothesis` | Replaces manual guessing with deterministic rules |
| `generate_picerl_i_report()` | List of hypotheses | Formatted text / record | Human-readable, court-ready serialization |
| `to_dict()` | `IntentHypothesis` | Dictionary record | Lossless export; `consistency_score` remains integer |

### Glossary
- **AbductiveResult**: The output of an inference engine that applies Ockham’s Razor—selecting the explanation with the fewest assumptions that still accounts for the observed forensic artifacts.
- **Consistency Score (`consistency_score`)**: A whole-number index (0–100) representing the strength of a hypothesis. Because the module employs deterministic integer arithmetic, the score is immune to rounding errors and bitwise non-determinism.
- **Daubert Guarantee**: The module’s architectural promise that every inference is (1) auditable via public tables, (2) reproducible for identical inputs, and (3) falsifiable through the mandatory `what_would_falsify` field.
- **Deterministic Integer Arithmetic**: Mathematical operations restricted to integers. This eliminates the representation uncertainty associated with floating-point formats and ensures bitwise reproducibility across hardware.
- **Forensic Artifact (`source_artifact`)**: Any digital object—log entry, memory page, file hash—that serves as evidence. The module tracks the provenance of every artifact used to build a hypothesis.
- **IR Phase**: A discrete stage in the incident-response lifecycle, such as detection, analysis, or containment.
- **PICERL**: The SANS Institute six-phase incident-response model: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. The suffix “-I” denotes the explicit Intent-analysis layer added by this module.
- **PICERLMapper**: The rule engine that translates an IR phase into a PICERL-I phase. It contains no procedural logic; it is a static table.
- **Peircean Abduction**: A formal logic of hypothesis generation (C. S. Peirce). In this module, it is implemented as a deterministic mapping, not as subjective guesswork.
- **Eco Semiotics**: Umberto Eco’s theory of signs. Here, a “sign” is a forensic artifact, and its “meaning” is fixed by explicit module constants rather than by interpretive whim.
- **Gricean Implicature**: Paul Grice’s model of meaning-by-context. The module replicates this only through explicit contextual rules encoded in tables, never through tacit human judgment.

### 【Scientific Note】
> **Peirce, Eco, and Grice Are Not Mysticism**
> 
> The philosophical vocabulary used in this module is sometimes confused with literary criticism or occult speculation. In digital forensics, these terms function as **formal sensor analogies**:
> 
> 1. **Peircean abduction** operates like a smoke detector. When particulate density crosses a threshold (observed effect), the device outputs “probable fire” (hypothesis). The module’s abductive engine does the same: it reads an artifact, consults a deterministic table, and outputs the simplest valid hypothesis. No intuition is involved.
> 
> 2. **Eco’s semiotics** operates like a RFID label reader. A radio signal (signifier) is meaningless noise until the lookup table matches it to a package ID (signified). The module treats every `RECONNAISSANCE` marker or `LATERAL_MOVEMENT` trace as a tag whose meaning is defined by public constants, not by interpretive mysticism.
> 
> 3. **Gricean implicature** operates like a multi-sensor fusion array. If a motion sensor triggers and a door sensor opens, the fused context implies “unauthorized entry” via explicit correlation rules. The module derives attacker intent from combinations of artifacts using only the written rules in its tables.
> 
> Every operation is deterministic integer arithmetic on explicitly defined symbols. There are no oracles, no hidden conditionals, and no floating-point approximations.

---

**ESPAÑOL**

## ¿Qué es este módulo?
Este módulo es el motor de traducción determinista del conjunto forense VIGIA. Convierte las observaciones de las fases de Respuesta a Incidentes (IR) en hipótesis formales sobre la intención del atacante, estructuradas según el marco PICERL-I. En lugar de depender de código opaco o de la intuición humana, el módulo utiliza tablas de consulta públicas y constantes, además de campos obligatorios de falseabilidad. Cada resultado es reproducible: la misma evidencia digital siempre produce la misma puntuación de consistencia entera y la misma clasificación de hipótesis. Este diseño respalda directamente el estándar Daubert para evidencia científica en procesos legales.

### Conceptos clave

**Tabla 1. Estructura de datos principal: `IntentHypothesis`**
| Campo | Categoría de dato | Restricción | Propósito científico |
|-------|-------------------|-------------|----------------------|
| `intent_type` | Etiqueta simbólica | Una de las constantes del módulo (p. ej., `RECONNAISSANCE`) | Clasifica el objetivo táctico del intruso |
| `consistency_score` | Entero | 0 a 100, inclusive | Medida determinista del apoyo evidencial; se calcula sin operaciones de coma flotante |
| `what_would_falsify` | Texto | Cadena no vacía obligatoria | Cumple el requisito Daubert de falseabilidad al establecer qué evidencia podría refutar la hipótesis |
| `source_artifact` | Identificador | Hash, serie de registro o ruta de archivo | Procedencia del artefacto forense que disparó la hipótesis |

**Tabla 2. Filosofía de mapeo: de IR a PICERL-I**
| Entrada (Fase IR) | Salida (Fase PICERL-I) | Mecanismo |
|-------------------|------------------------|-----------|
| Detección y análisis focalizado | IDENTIFICATION | Búsqueda determinista en tabla (`PICERLMapper`) |
| Resultado de inferencia abductiva (motor Ockham) | HIPÓTESIS DE INTENCIÓN | Traducción dirigida por tablas (`map_abductive_result`) |

**Tabla 3. Constantes auditable del módulo (lista parcial)**
| Constante | Denotación |
|-----------|------------|
| `RECONNAISSANCE` | Recolección de información pre-ataque |
| `INITIAL_ACCESS` | Vector de entrada inicial al sistema objetivo |
| `EXECUTION` | Ejecución de código malicioso |
| `PERSISTENCE` | Mantenimiento del acceso tras reinicios |
| `PRIVILEGE_ESCALATION` | Obtención de permisos de nivel superior |
| `DEFENSE_EVASION` | Evasión de herramientas de detección |
| `CREDENTIAL_ACCESS` | Robo de contraseñas o tokens |
| `DISCOVERY` | Mapeo de red posterior al compromiso |
| `LATERAL_MOVEMENT` | Movimiento entre hosts |
| `COLLECTION` | Agregación de datos para exfiltración |

**Tabla 4. Funciones públicas**
| Función | Entrada | Salida | Garantía |
|---------|---------|--------|----------|
| `map_focus_analysis_to_intent()` | Enumeración `IRPhase` | `IntentHypothesis` | Usa solo tablas de consulta; sin lógica condicional oculta (P0-3) |
| `map_abductive_result()` | `AbductiveResult` (Ockham) | `IntentHypothesis` | Reemplaza la conjetura manual con reglas deterministas |
| `generate_picerl_i_report()` | Lista de hipótesis | Texto / registro formateado | Serialización legible y apta para tribunales |
| `to_dict()` | `IntentHypothesis` | Registro diccionario | Exportación sin pérdida; `consistency_score` permanece como entero |

### Glosario
- **AbductiveResult**: Salida de un motor de inferencia que aplica la Navaja de Ockham: selecciona la explicación con menos supuestos que aún explique los artefactos forenses observados.
- **Consistency Score (`consistency_score`)**: Índice numérico entero (0–100) que representa la fuerza de una hipótesis. Al emplear aritmética entera determinista, la puntuación es inmune a errores de redondeo.
- **Garantía Daubert**: Promesa arquitectónica de que toda inferencia es (1) auditable mediante tablas públicas, (2) reproducible ante entradas idénticas, y (3) falseable gracias al campo obligatorio `what_would_falsify`.
- **Aritmética entera determinista**: Operaciones matemáticas restringidas a números enteros. Eliminan la incertidumbre de representación asociada a los formatos de coma flotante y garantizan reproducibilidad binaria entre distintos equipos.
- **Artefacto forense (`source_artifact`)**: Cualquier objeto digital—entrada de registro, página de memoria, hash de archivo—que sirve como evidencia. El módulo rastrea la procedencia de cada artefacto usado para construir una hipótesis.
- **Fase IR**: Etapa discreta del ciclo de vida de la respuesta a incidentes, como detección, análisis o contención.
- **PICERL**: Modelo de respuesta a incidentes de seis fases del Instituto SANS: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. El sufijo “-I” denota la capa explícita de análisis de intención añadida por este módulo.
- **PICERLMapper**: Motor de reglas que traduce una fase IR en una fase PICERL-I. No contiene lógica procedimental; es una tabla estática.
- **Abducción peirceana**: Lógica formal de generación de hipótesis (C. S. Peirce). En este módulo se implementa como un mapeo determinista, no como conjetura subjetiva.
- **Semiótica de Eco**: Teoría de los signos de Umberto Eco. Aquí, un “signo” es un artefacto forense, y su “significado” está fijado por constantes explícitas del módulo, no por capricho interpretativo.
- **Implicatura griceana**: Modelo de Paul Grice sobre el significado por contexto. El módulo lo replica solo a través de reglas contextuales explícitas codificadas en tablas, nunca mediante juicio humano tácito.

### 【Nota Científica】
> **Peirce, Eco y Grice no son misticismo**
> 
> El vocabulario filosófico empleado en este módulo suele confundirse con crítica literaria o especulación oculta. En forense digital, estos términos funcionan como **analogías formales de sensores**:
> 
> 1. La **abducción peirceana** opera como un detector de humo. Cuando la densidad de partículas cruza un umbral (efecto observado), el dispositivo emite “probable incendio” (hipótesis). El motor abductivo del módulo hace lo mismo: lee un artefacto, consulta una tabla determinista y emite la hipótesis válida más simple. No interviene la intuición.
> 
> 2. La **semiótica de Eco** opera como un lector de etiquetas RFID. Una señal de radio (significante) es ruido sin sentido hasta que la tabla de consulta la empareja con un identificador de paquete (significado). El módulo trata cada marcador `RECONNAISSANCE` o rastro `LATERAL_MOVEMENT` como una etiqueta cuyo significado se define por constantes públicas, no por misticismo interpretativo.
> 
> 3. La **implicatura griceana** opera como una red de fusión de sensores. Si un sensor de movimiento se activa y uno de puertas se abre, el contexto fusionado implica “entrada no autorizada” mediante reglas de correlación explícitas. El módulo deriva la intención del atacante a partir de combinaciones de artefactos usando únicamente las reglas escritas en sus tablas.
> 
> Cada operación es aritmética entera determinista sobre símbolos definidos explícitamente. No hay oráculos, no hay condicionales ocultos ni aproximaciones de coma flotante.

---

**РУССКИЙ**

## Что представляет собой этот модуль?
Этот модуль — детерминистский трансляционный движок судебно-медицинского комплекса VIGIA. Он преобразует наблюдения из фаз реагирования на инциденты (IR) в формальные гипотезы о намерениях злоумышленника, структурированные в рамках PICERL-I. Вместо непрозрачного кода или человеческой интуиции модуль использует открытые таблицы поиска с константами и обязательные поля фальсифицируемости. Каждый результат воспроизводим: одни и те же цифровые доказательства всегда дают одно и то же целочисленное значение согласованности и одну и ту же классификацию гипотезы. Такая архитектура напрямую поддерживает стандарт Доберта для научных доказательств в судебных разбирательствах.

### Ключевые понятия

**Таблица 1. Основная структура данных: `IntentHypothesis`**
| Поле | Категория данных | Ограничение | Научное назначение |
|------|------------------|-------------|--------------------|
| `intent_type` | Символическая метка | Одна из констант модуля (например, `RECONNAISSANCE`) | Классифицирует тактическую цель нарушителя |
| `consistency_score` | Целое число | От 0 до 100 включительно | Детерминистическая мера доказательной поддержки; вычисляется без операций с плавающей запятой |
| `what_would_falsify` | Текст | Обязательная непустая строка | Удовлетворяет требованию Доберта о фальсифицируемости, указывая, какое доказательство может опровергнуть гипотезу |
| `source_artifact` | Идентификатор | Хеш, серийный номер журнала или путь к файлу | Происхождение судебного артефакта, вызвавшего гипотезу |

**Таблица 2. Философия отображения: от IR к PICERL-I**
| Вход (фаза IR) | Выход (фаза PICERL-I) | Механизм |
|----------------|------------------------|----------|
| Обнаружение и фокусный анализ | IDENTIFICATION | Детерминистический поиск по таблице (`PICERLMapper`) |
| Результат абдуктивного вывода (движок Оккама) | ГИПОТЕЗА НАМЕРЕНИЯ | Табличная трансляция (`map_abductive_result`) |

**Таблица 3. Аудируемые константы модуля (частичный список)**
| Константа | Обозначение |
|-----------|-------------|
| `RECONNAISSANCE` | Сбор информации перед атакой |
| `INITIAL_ACCESS` | Первоначальный вектор проникновения |
| `EXECUTION` | Запуск вредоносного кода |
| `PERSISTENCE` | Сохранение доступа после перезагрузки |
| `PRIVILEGE_ESCALATION` | Получение привилегий более высокого уровня |
| `DEFENSE_EVASION` | Уклонение от средств обнаружения |
| `CREDENTIAL_ACCESS` | Кража паролей или токенов |
| `DISCOVERY` | Картографирование сети после компрометации |
| `LATERAL_MOVEMENT` | Перемещение между узлами |
| `COLLECTION` | Агрегирование данных для эксфильтрации |

**Таблица 4. Открытые функции**
| Функция | Вход | Выход | Гарантия |
|---------|------|-------|----------|
| `map_focus_analysis_to_intent()` | Перечисление `IRPhase` | `IntentHypothesis` | Использует только таблицы поиска; нет скрытой условной логики (P0-3) |
| `map_abductive_result()` | `AbductiveResult` (Оккам) | `IntentHypothesis` | Заменяет ручное угадывание детерминистическими правилами |
| `generate_picerl_i_report()` | Список гипотез | Форматированный текст / запись | Человекочитаемая сериализация, пригодная для суда |
| `to_dict()` | `IntentHypothesis` | Словарная запись | Беспотерянный экспорт; `consistency_score` остаётся целым числом |

### Глоссарий
- **AbductiveResult**: Выход инференсного движка, применяющего бритву Оккама — выбор объяснения с наименьшим числом допущений, которое тем не менее учитывает наблюдаемые судебные артефакты.
- **Consistency Score (`consistency_score`)**: Целочисленный индекс (0–100), представляющий силу гипотезы. Поскольку модуль использует детерминистическую целочисленную арифметику, показатель защищён от ошибок округления.
- **Гарантия Доберта (Daubert Guarantee)**: Архитектурное обязательство, что каждый вывод (1) аудируется через открытые таблицы, (2) воспроизводим при идентичных входных данных, (3) фальсифицируем благодаря обязательному полю `what_would_falsify`.
- **Детерминистическая целочисленная арифметика**: Математические операции, ограниченные целыми числами. Они устраняют неопределённость представления, присущую форматам с плавающей запятой, и гарантируют битовую воспроизводимость на разном оборудовании.
- **Судебный артефакт (`source_artifact`)**: Любой цифровой объект — запись журнала, страница памяти, хеш файла — служащий доказательством. Модуль отслеживает происхождение каждого артефакта, использованного для построения гипотезы.
- **Фаза IR (IR Phase)**: Дискретный этап жизненного цикла реагирования на инцидент: обнаружение, анализ, сдерживание и т.д.
- **PICERL**: Шестифазная модель реагирования на инциденты Института SANS: Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned. Суффикс «-I» обозначает явный слой анализа намерений, добавленный данным модулем.
- **PICERLMapper**: Правиловой движок, переводящий фазу IR в фазу PICERL-I. Не содержит процедурной логики; представляет собой статическую таблицу.
- **Пирсовская абдукция (Peircean Abduction)**: Формальная логика генерации гипотез (Ч. С. Пирс). В данном модуле реализована как детерминистическое отображение, а не как субъективная догадка.
- **Семиотика Эко (Eco Semiotics)**: Теория знаков Умберто Эко. Здесь «знак» — это судебный артефакт, а его «значение» фиксируется явными константами м
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
