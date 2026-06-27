<!--
VIGIA Academic Documentation
Module: 8fa48c2f
Batch ID: vigia-doc-0097-8fa48c2f
Generated: 2026-05-20T14:56:47.865558+00:00
-->

# Module Documentation: `vigia/inference/abductive_reasoner_v2.py`

---

## ENGLISH

### What Is This Module?

This module is a deterministic inference engine for digital-forensic investigation. It codifies **abductive reasoning**—the logic of inferring the best explanation from incomplete evidence—into a mathematically rigorous, fully reproducible framework.

Instead of approximate real-number formats, the engine computes every score as an **exact rational number** (a signed integer numerator divided by a signed integer denominator). This guarantees that two analysts, anywhere in the world, will obtain bitwise-identical results from the same input, satisfying the **Daubert standard** for scientific evidence in court.

The module models forensic evidence as layered strata ranked by tampering resistance; it tracks the chain of reasoning in **immutable, write-once records**; and it applies hard veto rules to prevent **judicial hallucination** (computer-generated conclusions unsupported by physical evidence).

### Key Concepts

#### Table A: Foundational Data Structures

| Structure | Plain-Language Description | Deterministic Rule |
|---|---|---|
| `EvidenceLayer` | A stratum of forensic data (e.g., Memory, Network, Registry, Disk) ranked by how difficult it is to forge or alter. | Lower layers are harder to tamper with; the engine uses this ranking to adjudicate ties. |
| `OntologicalLevel` | Three rungs of inference abstraction: **TECHNIQUE** (how), **TACTIC** (what was done), **OBJECTIVE** (why). | Strict ordering: technique ≥ tactic ≥ objective. A hypothesis cannot be more certain at a higher level than at a lower one. |
| `ArtifactRecord` | A write-once, tamper-evident card describing one piece of digital evidence. Once created, it cannot be changed. | `frozen=True` enforces immutability after creation. |
| `HypothesisScores` | The exact rational scores assigned to a hypothesis at the three ontological levels. | Invariant: `technique_score` ≥ `tactic_score` ≥ `objective_score`. All values are exact fractions in the closed interval [0, 1]. |
| `DecisionTrace` | An unchangeable log of the entire reasoning chain. | Every final conclusion must be mechanically derived from this trace. |
| `InferenceStep` | One individual link in the Peircean reasoning chain stored inside the `DecisionTrace`. | Append-only; cannot be retroactively modified. |

#### Table B: Causal & Inversion Engines

| Engine / Score | Purpose | Guarantee |
|---|---|---|
| `CausalLink` | A directed bond stating that a specific artifact supports, undermines, or is neutral to a hypothesis. | Evaluated by integer-based consistency metrics. |
| `CausalClosureScore` (CCS) | The deterministic output of causal-closure analysis: a rational measure of how completely the evidence explains the hypothesis. | Computed from exact fractions; floats are barred by contract. |
| `CausalClosureEngine` | The canonical calculator for CCS. | Deterministic. Reproducible. Daubert-compliant. |
| `InversionCausalEngine` | Resolves contradictions between two evidence layers (e.g., Memory reports X, Disk reports not-X) using the **Causal Inversion Principle**. | Automatically selects the dominant layer or records the contradiction itself as evidence. |
| `InversionVerdict` | The formal outcome of an inversion analysis. | Immutable record. |
| `InversionAnalysis` | The structured result of comparing two layers under causal inversion. | Captures which layer dominated and why. |

#### Table C: Safety, Veto & Type Enforcement

| Component | Role | Rule |
|---|---|---|
| `AbstainConditionsEngine` | A gatekeeper that evaluates six hard conditions before any hypothesis is accepted. | If any condition fails, the engine issues a deterministic **ABSTAIN** verdict to prevent hallucination. |
| `AbstainReason` | A catalog of exact, machine-readable codes explaining why the engine refused to decide. | Codes are integers, removing linguistic ambiguity. |
| `AbstainCheck` | The result of checking one veto condition. | The `trigger` field is boolean; no probabilistic confidence is used. |
| `enforce_fraction()` | A mandatory type barrier: any computed score must be an exact `Fraction` object. | Raises a detailed assertion failure if a float is detected. |
| `assert_range_01()` | A secondary barrier: every score must lie in the closed interval [0, 1]. | Integer bounds check (numerator ≥ 0, numerator ≤ denominator). |
| `check_all()` | Executes the four hard veto conditions plus two additional technical conditions. | Returns a list of `AbstainCheck`; if any `trigger` is true, the hypothesis is barred. |
| `is_admissible()` | Admissibility predicate. | A hypothesis is admissible **if and only if** CCS > 1/2 **and** no abstain condition is triggered. |

#### Table D: Abductive Phases (Peircean–Eco–Gricean Semiotics)

| Phase | Function | Sensor Analogy |
|---|---|---|
| `phase_firstness()` | Catalogues what is observed versus what is absent (Eco's *Significant Silence*). | **Raw detection:** A sensor reports a value, or its absence is noted as a distinct event rather than empty noise. |
| `phase_secondness()` | Evaluates each detected signal only against its expected baseline. | **Calibration:** The reading is judged abnormal or normal relative to a control baseline. |
| `phase_thirdness()` | Selects the hypothesis that requires the fewest unobserved entities (Occam's razor). | **Model selection:** The simplest model that explains all sensor readings is chosen. |

#### Table E: Computation & Resolution API

| Function | Purpose | Deterministic Mechanism |
|---|---|---|
| `compute()` | Calculates the canonical CCS from a list of evaluated `CausalLink` objects. | Pure integer rational arithmetic over numerators and denominators. |
| `compute_from_artifacts()` | Calculates CCS directly from a bundle of artifacts and a consistency map. | Bypasses intermediate link objects; still returns exact fractions. |
| `resolve()` | Resolves contradictions between Memory and Disk narratives. | Applies the dominance constants (`MEMORY_DOMINATES`, `DISK_DOMINATES`, or `CONTRADICTION_IS_EVIDENCE`). |
| `all_gaps()` | Enumerates missing or broken causal connections. | Returns a structured list of logical discontinuities. |

#### Table F: Validation Test Suite

| Test Function | Scenario Validated |
|---|---|
| `test_epistemic_weights_are_fractions()` | Confirms that all epistemic weights are exact fractions, never floats. |
| `test_ccs_canonical_formula()` | Document #1 case: `win_update.exe`. Memory (9/10) and Disk (4/10) consistency links correctly sum into the CCS numerator. |
| `test_ccs_with_missing_link()` | Document #2 case: `win_update.exe` with a **broken link** (Parent PID missing). Verifies graceful handling of missing causal bonds. |
| `test_ccs_below_threshold()` | Confirms that CCS ≤ 1/2 forces a deterministic **ABSTAIN**. |
| `test_inversion_principle()` | Validates that the causal inversion engine resolves layer conflicts correctly. |
| `test_abstain_conditions()` | Exercises the four hard veto conditions against known-bad inputs. |
| `test_hypothesis_monotonicity()` | Checks that adding consistent evidence never lowers a hypothesis score. |
| `test_hypothesis_monotonicity_violation()` | Checks that the engine detects and rejects non-monotonic updates. |
| `test_full_pipeline_win_update()` | End-to-end integration test using the Document #1 `win_update.exe` scenario. |

#### Table G: Canonical Constants

| Constant | Domain | Meaning |
|---|---|---|
| `MEMORY`, `NETWORK`, `REGISTRY`, `DISK_MFT` | `EvidenceLayer` | The four canonical forensic strata, ordered by decreasing volatility and increasing tampering resistance. |
| `TECHNIQUE`, `TACTIC`, `OBJECTIVE` | `OntologicalLevel` | The three strict inference rungs. |
| `MEMORY_DOMINATES` | Inversion rule | When true, Memory narratives prevail over Disk in a contradiction. |
| `DISK_DOMINATES` | Inversion rule | When true, Disk narratives prevail over Memory. |
| `CONTRADICTION_IS_EVIDENCE` | Inversion rule | When true, the contradiction itself is treated as a first-class evidence artifact rather than resolved by suppression. |

### Glossary

| Term | Definition |
|---|---|
| **Abduction** | The logic of inferring the most plausible cause from observed effects. |
| **Causal Closure Score (CCS)** | A rational number measuring the completeness of causal explanation. The admissibility threshold is CCS > 1/2. |
| **Daubert-compliant** | Satisfies the legal standard that scientific evidence must be testable, peer-reviewable, have a known error rate, and be generally accepted. |
| **Deterministic Integer Arithmetic** | Calculations performed with exact fractions (pairs of integers: numerator and denominator), eliminating rounding errors and ensuring bitwise reproducibility. |
| **Evidence Layer** | A class of forensic data source ordered by tampering resistance. |
| **Frozen Record** | An immutable data object that cannot be modified after creation, functioning like a write-once optical disc. |
| **Judicial Hallucination** | A computer-generated conclusion that lacks support in physical evidence, analogous to a false positive in an unvalidated assay. |
| **Ontological Level** | A tier of inferential abstraction; higher tiers subsume lower ones. |
| **Peircean Chain** | A linked sequence of abductive, deductive, and inductive steps modeled on Charles Sanders Peirce's semiotics. |
| **Significant Silence (Eco)** | The deliberate interpretation of missing evidence as informative, not merely as a null reading. |
| **Veto Condition** | A hard rule that, when violated, forces the engine to abstain from rendering a conclusion. |

### 【Scientific Note】

The terminology of Peirce, Eco, and Grice is not mysticism; it is formal epistemology dressed in historical vocabulary. In this module, these concepts operate as deterministic constraints on a logical sensor network. Think of the forensic workstation as a black-box laboratory instrument:

- Peirce's three phases (firstness, secondness, thirdness) correspond to the operating states of any calibrated sensor: raw detection, differential comparison against baseline, and model selection.
- Eco's "Significant Silence" is equivalent to distinguishing a sensor's null return ("zero") from an absence of measurement ("no data"). A broken wire is not the same as a zero reading; the module treats missing links as structurally informative events, not as empty cells.
- Gricean implicature functions like protocol logic for dropped sensor packets: if a signal is expected under hypothesis H but absent, the module records an implicature that counts against H through exact integer arithmetic.

There are no séances, no hermeneutic circles, and no Bayesian priors requiring subjective belief. The system is a deterministic finite-state machine whose transitions are governed by exact rational fractions. The philosophical labels are merely historical names for operations that any reproducible measurement device must perform.

---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es un motor de inferencia determinista para la investigación forense digital. Codifica el **razonamiento abductivo**—la lógica de inferir la mejor explicación a partir de evidencia incompleta—en un marco matemáticamente riguroso y totalmente reproducible.

En lugar de utilizar números de punto flotante aproximados, el motor calcula cada puntuación como un **número racional exacto** (una razón entre dos enteros). Esto garantiza que dos analistas, en cualquier parte del mundo, obtendrán resultados idénticos bit a bit a partir de la misma entrada, satisfaciendo el **estándar Daubert** para evidencia científica en tribunales.

El módulo modela la evidencia forense como estratos ordenados por resistencia a la manipulación; rastrea la cadena de razonamiento en **registros inmutables de escritura única**; y aplica reglas duras de veto para prevenir la **alucinación judicial** (conclusiones generadas por computadora sin sustento en evidencia física).

### Conceptos clave

#### Tabla A: Estructuras de datos fundamentales

| Estructura | Descripción en lenguaje sencillo | Regla determinista |
|---|---|---|
| `EvidenceLayer` | Estrato de datos forenses (p. ej., Memoria, Red, Registro, Disco) clasificado por dificultad de falsificación. | Las capas inferiores son más difíciles de alterar; el motor usa este orden para resolver empates. |
| `OntologicalLevel` | Tres peldaños de abstracción inferencial: **TECHNIQUE** (cómo), **TACTIC** (qué se hizo), **OBJECTIVE** (por qué). | Orden estricto: técnica ≥ táctica ≥ objetivo. Una hipótesis no puede ser más cierta en un nivel superior que en uno inferior. |
| `ArtifactRecord` | Tarjeta de escritura única que describe una pieza de evidencia digital. Una vez creada, no puede modificarse. | `frozen=True` impone inmutabilidad tras la creación. |
| `HypothesisScores` | Las puntuaciones racionales exactas asignadas a una hipótesis en los tres niveles ontológicos. | Invariante: `technique_score` ≥ `tactic_score` ≥ `objective_score`. Todos los valores son fracciones exactas en [0, 1]. |
| `DecisionTrace` | Registro inmutable de toda la cadena de razonamiento. | Toda conclusión final debe derivarse mecánicamente de esta traza. |
| `InferenceStep` | Un eslabón individual en la cadena de razonamiento peirciana. | Solo de adición; no puede modificarse retroactivamente. |

#### Tabla B: Motores causales y de inversión

| Motor / Puntuación | Propósito | Garantía |
|---|---|---|
| `CausalLink` | Vínculo dirigido que establece que un artefacto específico apoya, contradice o es neutral respecto a una hipótesis. | Evaluado por métricas de consistencia basadas en enteros. |
| `CausalClosureScore` (CCS) | Medida racional de cuán completamente la evidencia explica la hipótesis. | Calculado con fracciones exactas; los flotantes están excluidos por contrato. |
| `CausalClosureEngine` | Calculador canónico del CCS. | Determinista. Reproducible. Conforme a Daubert. |
| `InversionCausalEngine` | Resuelve contradicciones entre capas de evidencia usando el **Principio de Inversión Causal**. | Selecciona la capa dominante o registra la propia contradicción como evidencia. |
| `InversionVerdict` | Resultado formal de un análisis de inversión. | Registro inmutable. |
| `InversionAnalysis` | Resultado estructurado de la comparación de dos capas bajo inversión causal. | Captura qué capa dominó y por qué. |

#### Tabla C: Seguridad, veto y verificación de tipos

| Componente | Rol | Regla |
|---|---|---|
| `AbstainConditionsEngine` | Guardián que evalúa seis condiciones duras antes de aceptar cualquier hipótesis. | Si alguna condición falla, emite un veredicto **ABSTAIN** determinista. |
| `AbstainReason` | Catálogo de códigos exactos y legibles por máquina que explican por qué el motor se abstuvo. | Los códigos son enteros, eliminando ambigüedad lingüística. |
| `AbstainCheck` | Resultado de verificar una condición de veto. | El campo `trigger` es booleano; sin confianza probabilística. |
| `enforce_fraction()` | Barrera de tipos obligatoria: cualquier puntuación calculada debe ser un `Fraction` exacto. | Genera un fallo de aserción detallado si se detecta un flotante. |
| `assert_range_01()` | Barrera secundaria: toda puntuación debe estar en el intervalo cerrado [0, 1]. | Verificación de límites enteros. |
| `check_all()` | Ejecuta cuatro condiciones de veto duras más dos condiciones técnicas adicionales. | Devuelve una lista de `AbstainCheck`; si algún `trigger` es verdadero, la hipótesis es rechazada. |
| `is_admissible()` | Predicado de admisibilidad. | Una hipótesis es admisible **si y solo si** CCS > 1/2 **y** ninguna condición de abstención se activa. |

#### Tabla D: Fases abductivas (Semiótica Peirce–Eco–Grice)

| Fase | Función | Analogía con sensor |
|---|---|---|
| `phase_firstness()` | Cataloga lo observado frente a lo ausente (*Silencio Significativo* de Eco). | **Detección bruta:** El sensor reporta un valor, o su ausencia se registra como evento distinto. |
| `phase_secondness()` | Evalúa cada señal detectada contra su línea base esperada. | **Calibración:** La lectura se juzga normal o anormal respecto al control. |
| `phase_thirdness()` | Selecciona la hipótesis que requiere el menor número de entidades no observadas (navaja de Occam). | **Selección de modelo:** Se elige el modelo más simple que explica todas las lecturas del sensor. |

#### Tabla E: API de cómputo y resolución

| Función | Propósito | Mecanismo determinista |
|---|---|---|
| `compute()` | Calcula el CCS canónico a partir de una lista de `CausalLink` evaluados. | Aritmética racional entera pura. |
| `compute_from_artifacts()` | Calcula el CCS directamente desde un conjunto de artefactos y un mapa de consistencia. | Omite objetos de enlace intermedios; devuelve fracciones exactas. |
| `resolve()` | Resuelve contradicciones entre narrativas de Memoria y Disco. | Aplica las constantes de dominancia. |
| `all_gaps()` | Enumera conexiones causales faltantes o rotas. | Devuelve una lista estructurada de discontinuidades lógicas. |

#### Tabla F: Suite de pruebas de validación

| Función de prueba | Escenario validado |
|---|---|
| `test_epistemic_weights_are_fractions()` | Confirma que todos los pesos epistémicos son fracciones exactas, nunca flotantes. |
| `test_ccs_canonical_formula()` | Caso Documento #1: `win_update.exe`. Vínculos de consistencia de Memoria (9/10) y Disco (4/10). |
| `test_ccs_with_missing_link()` | Caso Documento #2: `win_update.exe` con **enlace roto** (PID padre faltante). |
| `test_ccs_below_threshold()` | Confirma que CCS ≤ 1/2 fuerza un **ABSTAIN** determinista. |
| `test_inversion_principle()` | Valida que el motor de inversión causal resuelve conflictos de capa correctamente. |
| `test_abstain_conditions()` | Ejercita las cuatro condiciones de veto duras. |
| `test_hypothesis_monotonicity()` | Comprueba que añadir evidencia consistente nunca baja una puntuación. |
| `test_hypothesis_monotonicity_violation()` | Comprueba que el motor detecta y rechaza actualizaciones no monótonas. |
| `test_full_pipeline_win_update()` | Prueba de integración de extremo a extremo con el escenario `win_update.exe`. |

#### Tabla G: Constantes canónicas

| Constante | Dominio | Significado |
|---|---|---|
| `MEMORY`, `NETWORK`, `REGISTRY`, `DISK_MFT` | `EvidenceLayer` | Los cuatro estratos forenses canónicos. |
| `TECHNIQUE`, `TACTIC`, `OBJECTIVE` | `OntologicalLevel` | Los tres peldaños de inferencia estrictos. |
| `MEMORY_DOMINATES` | Regla de inversión | Prevalece la narrativa de Memoria sobre Disco en contradicción. |
| `DISK_DOMINATES` | Regla de inversión | Prevalece la narrativa de Disco sobre Memoria. |
| `CONTRADICTION_IS_EVIDENCE` | Regla de inversión | La contradicción misma se trata como artefacto de evidencia. |

### Glosario

| Término | Definición |
|---|---|
| **Abducción** | Lógica de inferir la causa más plausible a partir de efectos observados. |
| **Puntuación de Cierre Causal (CCS)** | Número racional que mide la completitud de la explicación causal. Umbral: CCS > 1/2. |
| **Conforme a Daubert** | Satisface el estándar legal de evidencia científica: verificable, revisable por pares, con tasa de error conocida. |
| **Aritmética Entera Determinista** | Cálculos con fracciones exactas (pares de enteros), eliminando errores de redondeo. |
| **Capa de evidencia** | Clase de fuente de datos forenses ordenada por resistencia a la manipulación. |
| **Registro inmutable** | Objeto de datos que no puede modificarse tras su creación, como un disco óptico de escritura única. |
| **Alucinación judicial** | Conclusión generada por computadora sin sustento en evidencia física. |
| **Nivel ontológico** | Nivel de abstracción inferencial; los niveles superiores subsumen los inferiores. |
| **Cadena peirciana** | Secuencia vinculada de pasos abductivos, deductivos e inductivos. |
| **Silencio Significativo (Eco)** | Interpretación deliberada de la evidencia faltante como informativa, no como lectura nula. |
| **Condición de veto** | Regla dura que, al violarse, obliga al motor a abstenerse de emitir una conclusión. |

### 【Nota Científica】

La terminología de Peirce, Eco y Grice no es misticismo; es epistemología formal vestida en vocabulario histórico. En este módulo, estos conceptos operan como restricciones deterministas sobre una red lógica de sensores. Piense en la estación de trabajo forense como un instrumento de laboratorio de caja negra:

- Las tres fases de Peirce (primeridad, segundidad, terceridad) corresponden a los estados operativos de cualquier sensor calibrado: detección bruta, comparación diferencial contra línea base, y selección de modelo.
- El "Silencio Significativo" de Eco equivale a distinguir el retorno nulo de un sensor ("cero") de la ausencia de medición ("sin datos"). Un cable roto no es lo mismo que una lectura cero; el módulo trata los enlaces faltantes como eventos estructuralmente informativos.
- La implicatura de Grice funciona como lógica de protocolo para paquetes de sensor perdidos: si se espera una señal bajo la hipótesis H pero está ausente, el módulo registra una implicatura que cuenta en contra de H mediante aritmética entera exacta.

No hay séances, círculos hermenéuticos ni priors bayesianas que requieran creencia subjetiva. El sistema es una máquina de estados finitos determinista cuyas transiciones se rigen por fracciones racionales exactas.

---

## РУССКИЙ

### Что представляет собой этот модуль?

Этот модуль — детерминистский механизм логического вывода для цифровой криминалистики. Он формализует **абдуктивное рассуждение** — логику вывода наилучшего объяснения из неполных доказательств — в математически строгую и полностью воспроизводимую систему.

Вместо приближённых чисел с плавающей запятой движок вычисляет каждую оценку в виде **точной рациональной дроби** (отношения двух целых чисел). Это гарантирует, что два эксперта в любой точке мира получат побитово идентичные результаты по одним и тем же входным данным, удовлетворяя **стандарту Daubert** для судебной научной экспертизы.

Модуль представляет криминалистические доказательства в виде упорядоченных по устойчивости к подделке слоёв; фиксирует цепочку рассуждений в **неизменяемых записях с однократной записью**; и применяет жёсткие правила вето для предотвращения **«судебной галлюцинации»** (компьютерных заключений, не подкреплённых физическими доказательствами).

### Ключевые концепции

#### Таблица А: Базовые структуры данных

| Структура | Описание простым языком | Детерминированное правило |
|---|---|---|
| `EvidenceLayer` | Страт криминалистических данных (напр., Память, Сеть, Реестр, Диск), упорядоченный по трудности фальсификации. | Нижние уровни сложнее изменить; движок использует этот порядок для разрешения ничьих. |
| `OntologicalLevel` | Три ступени абстракции вывода: **TECHNIQUE** (как), **TACTIC** (что было сделано), **OBJECTIVE** (зачем). | Строгий порядок: техника ≥ тактика ≥ цель. Гипотеза не может быть более достоверной на высшем уровне, чем на низшем. |
| `ArtifactRecord` | Карточка однократной записи, описывающая один фрагмент цифрового доказательства. После создания не может изменяться. | `frozen=True` обеспечивает неизменяемость после создания. |
| `HypothesisScores` | Точные рациональные оценки гипотезы на трёх онтологических уровнях. | Инвариант: `technique_score` ≥ `tactic_score` ≥ `objective_score`. Все значения — точные дроби в [0, 1]. |
| `DecisionTrace` | Неизменяемый журнал всей цепочки рассуждений. | Каждый итоговый вывод должен механически следовать из этой трассировки. |
| `InferenceStep` | Одно звено пирсовской цепочки рассуждений внутри `DecisionTrace`. | Только добавление; не может быть изменено ретроспективно. |

#### Таблица Б: Причинные и инверсионные движки

| Движок / Оценка | Назначение | Гарантия |
|---|---|---|
| `CausalLink` | Направленная связь, утверждающая, что конкретный артефакт поддерживает, опровергает или нейтрален к гипотезе. | Оценивается по целочисленным метрикам согласованности. |
| `CausalClosureScore` (CCS) | Рациональная мера полноты причинного объяснения. | Вычисляется из точных дробей; числа с плавающей запятой запрещены контрактом. |
| `CausalClosureEngine` | Канонический калькулятор CCS. | Детерминированный. Воспроизводимый. Соответствует Daubert. |
| `InversionCausalEngine` | Разрешает противоречия между двумя слоями доказательств с помощью **Принципа причинной инверсии**. | Автоматически выбирает доминирующий слой или фиксирует само противоречие как доказательство. |
| `InversionVerdict` | Формальный результат инверсионного анализа. | Неизменяемая запись. |
| `InversionAnalysis` | Структурированный результат сравнения двух слоёв под причинной инверсией. | Фиксирует, какой слой доминировал и почему. |

#### Таблица В: Безопасность, вето и проверка типов

| Компонент | Роль | Правило |
|---|---|---|
| `AbstainConditionsEngine` | Страж, оценивающий шесть жёстких условий перед принятием любой гипотезы. | При сбое любого условия выдаёт детерминированный вердикт **ABSTAIN**. |
| `AbstainReason` | Каталог точных машиночитаемых кодов, объясняющих отказ движка от решения. | Коды — целые числа, устраняющие лингвистическую неоднозначность. |
| `AbstainCheck` | Результат проверки одного условия вето. | Поле `trigger` булево; вероятностная уверенность не используется. |
| `enforce_fraction()` | Обязательный барьер типов: любая вычисленная оценка должна быть точным объектом `Fraction`. | Генерирует подробный сбой утверждения при обнаружении числа с плавающей запятой. |
| `assert_range_01()` | Вторичный барьер: каждая оценка должна лежать в закрытом интервале [0, 1]. | Целочисленная проверка границ. |
| `check_all()` | Выполняет четыре жёстких условия вето плюс два дополнительных технических условия. | Возвращает список `AbstainCheck`; если любой `trigger` истинен, гипотеза отклоняется. |
| `is_admissible()` | Предикат допустимости. | Гипотеза допустима **тогда и только тогда, когда** CCS > 1/2 **и** ни одно условие воздержания не активировано. |

#### Таблица Г: Абдуктивные фазы (Семиотика Пирс–Эко–Грайс)

| Фаза | Функция | Аналогия с датчиком |
|---|---|---|
| `phase_firstness()` | Каталогизирует наблюдаемое и отсутствующее (*Значимое молчание* Эко). | **Сырое обнаружение:** Датчик сообщает значение, или его отсутствие фиксируется как отдельное событие. |
| `phase_secondness()` | Оценивает каждый обнаруженный сигнал только относительно ожидаемой базовой линии. | **Калибровка:** Показание признаётся нормальным или аномальным относительно контрольной базовой линии. |
| `phase_thirdness()` | Выбирает гипотезу, требующую наименьшего числа ненаблюдаемых сущностей (бритва Оккама). | **Выбор модели:** Выбирается простейшая модель, объясняющая все показания датчика. |

#### Таблица Д: API вычислений и разрешения

| Функция | Назначение | Детерминированный механизм |
|---|---|---|
| `compute()` | Вычисляет канонический CCS из списка оценённых объектов `CausalLink`. | Чистая целочисленная рациональная арифметика. |
| `compute_from_artifacts()` | Вычисляет CCS непосредственно из набора артефактов и карты согласованности. | Обходит промежуточные объекты связи; по-прежнему возвращает точные дроби. |
| `resolve()` | Разрешает противоречия между нарративами Памяти и Диска. | Применяет константы доминирования. |
| `all_gaps()` | Перечисляет отсутствующие или разорванные причинные связи. | Возвращает структурированный список логических разрывов. |

### Глоссарий

| Термин | Определение |
|---|---|
| **Абдукция** | Логика вывода наиболее правдоподобной причины из наблюдаемых следствий. |
| **Оценка причинной замкнутости (CCS)** | Рациональное число, измеряющее полноту причинного объяснения. Порог допустимости: CCS > 1/2. |
| **Соответствие Daubert** | Удовлетворяет юридическому стандарту: научные доказательства должны быть проверяемыми, рецензируемыми, с известной частотой ошибок. |
| **Детерминированная целочисленная арифметика** | Вычисления с точными дробями (пары целых чисел), устраняющие ошибки округления. |
| **Слой доказательств** | Класс источника криминалистических данных, упорядоченный по устойчивости к фальсификации. |
| **Неизменяемая запись** | Объект данных, который не может быть изменён после создания. |
| **Судебная галлюцинация** | Компьютерный вывод, не подкреплённый физическими доказательствами. |
| **Онтологический уровень** | Уровень абстракции вывода; высшие уровни охватывают низшие. |
| **Пирсовская цепочка** | Связанная последовательность абдуктивных, дедуктивных и индуктивных шагов. |
| **Значимое молчание (Эко)** | Намеренная интерпретация отсутствующих доказательств как информативных. |
| **Условие вето** | Жёсткое правило, нарушение которого вынуждает движок воздержаться от вынесения заключения. |

### 【Научное примечание】

Терминология Пирса, Эко и Грайса — не мистицизм; это формальная эпистемология в историческом обличии. В данном модуле эти концепции функционируют как детерминированные ограничения на логическую сеть датчиков. Представьте судебную рабочую станцию как лабораторный инструмент-«чёрный ящик»:

- Три фазы Пирса (первичность, вторичность, третичность) соответствуют рабочим состояниям любого калиброванного датчика: сырое обнаружение, дифференциальное сравнение с базовой линией, выбор модели.
- «Значимое молчание» Эко эквивалентно различению нулевого возврата датчика («ноль») от отсутствия измерения («нет данных»). Обрыв провода — это не то же самое, что нулевое показание; модуль трактует недостающие звенья как структурно информативные события.
- Импликатура Грайса функционирует как логика протокола для потерянных пакетов датчика: если сигнал ожидается при гипотезе H, но отсутствует, модуль фиксирует импликатуру, засчитываемую против H через точную целочисленную арифметику.

Здесь нет спиритических сеансов, герменевтических кругов или байесовских априоров, требующих субъективной веры. Система — детерминированная машина конечных состояний, переходы которой определяются точными рациональными дробями.

---

## 中文

### 这是什么模块？

本模块是一个用于数字取证的确定性推理引擎。它将**溯因推理**（从不完整证据中推断最佳解释的逻辑）编码为数学上严格且完全可复现的框架。

引擎不使用近似浮点数，而是将每个评分计算为**精确有理数**（两个整数的比值）。这保证了全球任何两位分析师在相同输入下都会得到逐位一致的结果，满足法庭上科学证据的**道伯特（Daubert）标准**。

本模块将取证证据建模为按抗篡改能力排序的层级；用一次性写入的**不可变记录**追踪推理链；并应用硬性否决规则以防止"**司法幻觉**"（计算机生成但缺乏物理证据支持的结论）。

### 核心概念

#### 表 A：基础数据结构

| 结构 | 通俗描述 | 确定性规则 |
|---|---|---|
| `EvidenceLayer` | 按伪造难度排序的取证数据层（如内存、网络、注册表、磁盘）。 | 越底层越难篡改；引擎以此排名裁决平局。 |
| `OntologicalLevel` | 三个推理抽象层级：**TECHNIQUE**（如何）、**TACTIC**（做了什么）、**OBJECTIVE**（为何）。 | 严格排序：技术 ≥ 战术 ≥ 目标。假设在更高层级的确定性不能超过更低层级。 |
| `ArtifactRecord` | 描述一件数字证据的只写卡片。一旦创建，不可更改。 | `frozen=True` 在创建后强制执行不可变性。 |
| `HypothesisScores` | 在三个本体论层级上分配给假设的精确有理数评分。 | 不变量：`technique_score` ≥ `tactic_score` ≥ `objective_score`。所有值为闭区间 [0, 1] 内的精确分数。 |
| `DecisionTrace` | 整个推理链的不可变日志。 | 每个最终结论都必须从该轨迹中机械地推导出来。 |
| `InferenceStep` | 存储在 `DecisionTrace` 中的皮尔斯推理链的单个环节。 | 仅可追加；不能被追溯修改。 |

#### 表 B：因果与反转引擎

| 引擎 / 评分 | 用途 | 保证 |
|---|---|---|
| `CausalLink` | 表明特定取证工件支持、削弱或对假设中立的有向关联。 | 通过基于整数的一致性指标评估。 |
| `CausalClosureScore`（CCS） | 证据对假设解释完整性的有理数度量。 | 从精确分数计算；浮点数被合约禁止。 |
| `CausalClosureEngine` | CCS 的标准计算器。 | 确定性。可复现。符合道伯特标准。 |
| `InversionCausalEngine` | 使用**因果反转原则**解决两个证据层之间的矛盾。 | 自动选择主导层，或将矛盾本身记录为证据。 |
| `InversionVerdict` | 反转分析的正式结果。 | 不可变记录。 |
| `InversionAnalysis` | 在因果反转下比较两层的结构化结果。 | 记录哪层主导及其原因。 |

#### 表 C：安全、否决与类型执行

| 组件 | 角色 | 规则 |
|---|---|---|
| `AbstainConditionsEngine` | 在接受任何假设之前评估六个硬性条件的守门人。 | 任何条件失败时，发出确定性 **ABSTAIN** 裁决。 |
| `AbstainReason` | 解释引擎拒绝决策原因的精确机器可读代码目录。 | 代码为整数，消除语言歧义。 |
| `AbstainCheck` | 检查一个否决条件的结果。 | `trigger` 字段为布尔值；不使用概率置信度。 |
| `enforce_fraction()` | 强制类型屏障：任何计算评分必须是精确的 `Fraction` 对象。 | 若检测到浮点数则引发详细断言失败。 |
| `assert_range_01()` | 次级屏障：每个评分必须在闭区间 [0, 1] 内。 | 整数边界检查。 |
| `check_all()` | 执行四个硬性否决条件加两个额外技术条件。 | 返回 `AbstainCheck` 列表；若任何 `trigger` 为真，假设被拒绝。 |
| `is_admissible()` | 可采信性谓词。 | 假设可采信**当且仅当** CCS > 1/2 **且**未触发任何弃权条件。 |

#### 表 D：溯因阶段（皮尔斯–艾柯–格赖斯符号学）

| 阶段 | 功能 | 传感器类比 |
|---|---|---|
| `phase_firstness()` | 记录观测到的与缺失的内容（艾柯的*显著沉默*）。 | **原始检测：** 传感器报告一个值，或其缺失作为独立事件而非空噪声被记录。 |
| `phase_secondness()` | 仅根据预期基线评估每个检测到的信号。 | **校准：** 相对于控制基线，读数被判断为正常或异常。 |
| `phase_thirdness()` | 选择需要最少未观测实体的假设（奥卡姆剃刀）。 | **模型选择：** 选择解释所有传感器读数的最简模型。 |

#### 表 E：计算与解析 API

| 函数 | 用途 | 确定性机制 |
|---|---|---|
| `compute()` | 从已评估的 `CausalLink` 对象列表计算标准 CCS。 | 对分子和分母进行纯整数有理运算。 |
| `compute_from_artifacts()` | 直接从取证工件束和一致性映射计算 CCS。 | 绕过中间链接对象；仍返回精确分数。 |
| `resolve()` | 解决内存和磁盘叙述之间的矛盾。 | 应用主导常数。 |
| `all_gaps()` | 枚举缺失或断裂的因果连接。 | 返回逻辑断裂的结构化列表。 |

#### 表 F：验证测试套件

| 测试函数 | 验证场景 |
|---|---|
| `test_epistemic_weights_are_fractions()` | 确认所有认知权重为精确分数，从不为浮点数。 |
| `test_ccs_canonical_formula()` | 文档 #1 案例：`win_update.exe`。内存（9/10）与磁盘（4/10）一致性链接正确汇总进 CCS 分子。 |
| `test_ccs_with_missing_link()` | 文档 #2 案例：`win_update.exe` 存在**逻辑断裂**（父 PID 缺失）。验证对缺失因果键的优雅处理。 |
| `test_ccs_below_threshold()` | 确认 CCS ≤ 1/2 强制产生确定性 **ABSTAIN**。 |
| `test_inversion_principle()` | 验证因果反转引擎正确解决层级冲突。 |
| `test_abstain_conditions()` | 对已知错误输入执行四个硬性否决条件。 |
| `test_hypothesis_monotonicity()` | 检查添加一致证据不会降低假设评分。 |
| `test_hypothesis_monotonicity_violation()` | 检查引擎检测并拒绝非单调更新。 |
| `test_full_pipeline_win_update()` | 使用文档 #1 `win_update.exe` 场景的端到端集成测试。 |

#### 表 G：标准常量

| 常量 | 域 | 含义 |
|---|---|---|
| `MEMORY`、`NETWORK`、`REGISTRY`、`DISK_MFT` | `EvidenceLayer` | 四个标准取证层，按挥发性降低和抗篡改性增加排序。 |
| `TECHNIQUE`、`TACTIC`、`OBJECTIVE` | `OntologicalLevel` | 三个严格推理层级。 |
| `MEMORY_DOMINATES` | 反转规则 | 为真时，内存叙述在矛盾中优先于磁盘。 |
| `DISK_DOMINATES` | 反转规则 | 为真时，磁盘叙述优先于内存。 |
| `CONTRADICTION_IS_EVIDENCE` | 反转规则 | 为真时，矛盾本身被视为一级取证工件，而非通过抑制解决。 |

### 术语表

| 术语 | 定义 |
|---|---|
| **溯因推理** | 从观测到的效果推断最合理原因的逻辑。 |
| **因果闭合分数（CCS）** | 衡量因果解释完整性的有理数。可采信阈值：CCS > 1/2。 |
| **符合道伯特标准** | 满足科学证据的法律标准：可测试、可同行评审、有已知错误率且被普遍接受。 |
| **确定性整数运算** | 使用精确分数（整数对）进行计算，消除舍入误差，确保逐位可复现性。 |
| **取证层** | 按抗篡改能力排序的取证数据源类别。 |
| **不可变记录** | 创建后无法修改的数据对象，类似一次性写入光盘。 |
| **司法幻觉** | 缺乏物理证据支持的计算机生成结论。 |
| **本体论层级** | 推理抽象层；较高层级涵盖较低层级。 |
| **皮尔斯链条** | 基于皮尔斯符号学的溯因、演绎与归纳步骤的关联序列。 |
| **艾柯的显著沉默** | 将缺失证据有意解释为信息性内容，而非空读数。 |
| **否决条件** | 被违反时迫使引擎弃权的硬性规则。 |

### 【科学说明】

皮尔斯、艾柯与格赖斯的术语不是神秘主义，而是穿着历史词汇的形式认识论。在本模块中，这些概念作为逻辑传感器网络的确定性约束运作。将取证工作站想象为一台黑匣子实验室仪器：

- 皮尔斯的三个阶段（第一性、第二性、第三性）对应任何校准传感器的运行状态：原始检测、与基线的差异比较、模型选择。
- 艾柯的"显著沉默"等同于区分传感器的零返回（"零"）与测量缺失（"无数据"）。线路断裂与零读数不同；本模块将逻辑断裂视为结构性信息事件，而非空单元格。
- 格赖斯的含义理论（implicature）类似于对传感器丢包的协议逻辑：如果在假设 H 下预期出现信号但缺失，引擎通过精确整数运算记录一项不利于 H 的推导。

这里没有降神会、诠释学循环或需要主观信念的贝叶斯先验。该系统是一台确定性有限状态机，其转换由精确有理分数控制。这些哲学标签只是任何可复现测量设备都必须执行的操作的历史名称。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
