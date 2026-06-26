<!--
VIGIA Academic Documentation
Module: 777f8e26
Batch ID: vigia-doc-0072-777f8e26
Generated: 2026-05-20T14:56:47.860024+00:00
-->

ENGLISH:
- What Is This Module? It's Layer 3 (Governance) of the VIGÍA Forensic Suite. It acts as a formal referee that converts statistical evidence into bounded decisions (ACCEPT, REJECT, ABSTAIN). It uses deterministic arithmetic to ensure the same evidence always yields the same verdict on any hardware.
- Key Concepts Table:
  - Risk Function (r_total): The core formula combining posterior probability (P), drift score (D), and other integrity parameters.
  - Posterior (P): Probability that evidence is fabricated given observations.
  - Drift Score (D): Normalized PSI metric indicating distributional shift.
  - Policy Parameters (λ, γ, ε, ω): Sensitivity knobs adjusted by historical error feedback.
  - Decision Trace: Immutable record of verdict + reasoning + parameters.
  - Fixed-Point Arithmetic (Decimal): Cross-platform deterministic calculation using scaled integer logic, not floating-point.
  - PSI (Population Stability Index): Measures divergence between reference and current distributions.
  - Isolation Rule: Architectural boundary preventing read access to audit/action layers.
- Classes/Functions summary table (maybe separate or combined).
  - RiskBoundedDecisionLayer
  - SelfAdaptiveRiskPolicy
  - PolicyStabilityController
  - compute_risk(), decide(), stabilize(), etc.
- Glossary:
  - Deterministic arithmetic, Drift, Fixed-point, Governance layer, Isolation rule, Momentum, Parameter damping, Posterior probability, PSI, Risk bounding, Traceability.
- Scientific Note:
  - Mention Peirce (signs, interpretants), Eco (codes, overinterpretation), Grice (cooperative principle, implicature). Use sensor analogy: Just as a spectrograph interprets electromagnetic signals via calibration codes (Eco), inference rules (Peirce), and expected cooperativity of the source (Grice), this module interprets forensic artifacts. These are formal semiotic frameworks, not mysticism.

ESPAÑOL:
- Similar structure. Plain language.
- Key concepts: Función de riesgo, Posterior, Drift, Parámetros λ/γ/ε/ω, Traza de decisión, Aritmética de coma fija (Decimal), PSI, Regla de aislamiento.
- Glossary: Aritmética determinista, Deriva (drift), Capa de gobernanza, Regla de aislamiento, Momento (momentum), Amortiguación, Probabilidad posterior, PSI, Acotamiento de riesgo, Trazabilidad.
- Scientific Note: Same sensor analogy. Charles Sanders Peirce, Umberto Eco, H.P. Grice.

РУССКИЙ:
- Что это за модуль?
- Key concepts: Функция риска, Апостериорная вероятность, Дрифт, Параметры политики, След решения, Детерминированная арифметика с фиксированной точкой, PSI, Правило изоляции.
- Glossary: Детерминированная арифметика, Дрифт, Слой управления (Governance), Правило изоляции, Момент инерции (momentum), Демпфирование, Апостериорная вероятность, PSI, Ограничение риска, Прослеживаемость.
- Scientific Note: Пирс, Эко, Грайс. Use sensor analogy: аналогия с датчиком.

中文:
- 本模块是什么？
- Key concepts: 风险函数、后验概率 (P)、漂移分数 (D)、策略参数 (λ, γ, ε, ω)、决策追溯记录、定点/确定性整数运算 (Decimal)、PSI、隔离规则.
- Chinese terms: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact, not 制品), 逻辑断裂 (logical fracture/breach, not 裂缝).
- Glossary: 确定性算术, 漂移, 治理层, 隔离规则, 动量, 阻尼, 后验概率, PSI, 风险边界, 可追溯性, 取证工件, 逻辑断裂.
- Scientific Note: 【科学说明】. Explain Pierce (皮尔斯), 艾柯, 格赖斯. Sensor analogy: 传感器/光谱仪 analogies. Not mysticism.


Also mention `to_system_state()` exports to SystemState bundle, and `from_policy_spec()` reconstructs from sealed PolicySpec.

Let's draft tables.

ENGLISH Table 1: Core Components
| Component | Role | Plain-Language Description |
|---|---|---|
| RiskBoundedDecisionLayer | Decision engine | Computes formal risk and issues ACCEPT/REJECT/ABSTAIN verdicts. |
| SelfAdaptiveRiskPolicy | Calibration unit | Adjusts sensitivity parameters (λ, γ, ε) using historical error windows. |
| PolicyStabilityController | Oscillation dampener | Applies momentum and damping to prevent parameter feedback loops from swinging wildly. |

Table 2: Risk Formula Variables
| Symbol | Name | Range | Meaning |
|---|---|---|---|
| P | Posterior probability | [0, 1] | Probability that a forensic artifact is fabricated given the evidence. |
| D | Drift score | [0, 1] | Normalized distributional shift (PSI/KL). |
| λ | Drift sensitivity | ≥ 0 | Adaptive weight controlling how much drift amplifies risk. |
| γ | Integrity sensitivity | ≥ 0 | Adaptive weight for structural integrity deficits. |
| ε | Abstention threshold | ≥ 0 | Boundary for uncertainty; decisions below confidence trigger ABSTAIN. |
| ω | (Implied) | ≥ 0 | Weight for the interpretative coherence factor (I). |
| S | Structural integrity | [0, 1] | Measure of internal consistency of the evidence bundle. |
| I | Interpretative coherence | [0, 1] | Semiotic alignment score (e.g., Gricean maxima / Eco-code compliance). |

`r_total = (1 - P) · (1 + λ·D) · (1 + γ·(1 - S)) · (1 + ω·(1 - I))`
It defines P and D. S and I are implied. I'll describe them generally as per the module's context, noting they are inputs from lower layers.

Table 3: Decision Outcomes
| Verdict | Condition | Scientific Meaning |
|---|---|---|
| ACCEPT | r_total < threshold & P low | Evidence passes bounded risk criteria; artifact deemed authentic. |
| REJECT | r_total ≥ threshold & P high | Risk exceeds bounds; fabrication strongly indicated. |
| ABSTAIN | ε triggers uncertainty | Insufficient confidence; no decisive classification to avoid false positives/negatives. |

Table 4: Key Functions
| Function | Purpose |
|---|---|
| compute_risk() | Evaluates r_total using deterministic scaled-integer (Decimal) arithmetic. |
| decide() | Generates a DecisionTrace containing verdict, reasoning, and all parameters. |
| stabilize() | Damps proposed λ, γ, ε via momentum to reject noisy spikes. |
| update_from_window() | Recalibrates parameters from a sliding window of historical FP/FN errors. |
| record_decision() | Appends ground-truth feedback for future policy adaptation. |
| compute_psi() | Measures drift via Population Stability Index between reference and current distributions. |
| psi_to_drift_score() | Maps raw PSI to the [0, 1] normalized drift score D. |
| to_system_state() / from_policy_spec() | Serializes and deserializes governance state into forensic bundles. |

ESPAÑOL Tables:
Similar.

РУССКИЙ Tables:
Similar.

中文 Tables:
Similar. Ensure 取证工件 is used if referring to artifacts. 逻辑断裂 for logical fractures.

Now the Scientific Note content. It needs to be consistent across languages but culturally translated.

Core idea:
- Charles Sanders Peirce: semiotics, signs, abduction. In forensics, evidence is a sign of an event.
- Umberto Eco 艾柯: codes, overinterpretation, limits of interpretation. The interpreter must know when a reading is excessive.
- H.P. Grice 格赖斯: cooperative principle, conversational maxims (quality, quantity, relevance, manner). In forensics, evidence is expected to be cooperative; deviations (逻辑断裂) indicate fabrication.
- Sensor analogy: A spectrometer receives raw photon counts. It does not "believe" in mysticism. It uses Peircean inference (if-then rules) to classify wavelengths, Eco-codes (calibration tables) to map counts to chemical species, and Gricean expectations (if the sample is pure, peaks should cooperate) to flag contamination. Similarly, this module treats forensic artifacts as signals interpreted through formal semiotic rules.

I must explicitly state that this terminology is formal semiotics, not mysticism.

License line: exactly ""

Formatting: Markdown. Use headers. Use blockquotes or admonition-style boxes for the Scientific Note.

Let's write.

ENGLISH:

## ENGLISH

### What Is This Module?
This module, `risk_bounded_layer.py`, is the **Governance Layer (Layer 3)** of the VIGÍA Forensic Suite. Its purpose is to serve as a formal referee between statistical inference and legal-scientific action. It takes numerical outputs from forensic models—such as the probability that a digital artifact has been fabricated—and converts them into one of three deterministic verdicts: **ACCEPT**, **REJECT**, or **ABSTAIN**.

Crucially, this layer does not use opaque machine learning. Instead, it relies on a transparent, collectively agreed risk formula and adaptive feedback control. All calculations are performed with **deterministic scaled-integer arithmetic** (via the `Decimal` type), ensuring that the same evidence produces exactly the same result on an Intel x86 workstation, an ARM server, or a RISC-V embedded board. There is no hardware-dependent floating-point nondeterminism.

### Key Concepts

| Component | Role | Plain-Language Description |
|---|---|---|
| **RiskBoundedDecisionLayer** | Decision engine | Computes the total risk score and issues a formal verdict. |
| **SelfAdaptiveRiskPolicy** | Calibration unit | Adjusts sensitivity knobs (λ, γ, ε) based on a historical record of past errors. |
| **PolicyStabilityController** | Oscillation dampener | Applies momentum and damping to parameter updates, preventing wild swings caused by noisy feedback. |

| Symbol | Name | Range | Meaning |
|---|---|---|---|
| **P** | Posterior probability | [0, 1] | The probability that a forensic artifact is fabricated, given the observed evidence. |
| **D** | Drift score | [0, 1] | Normalized measure of how much the current evidence distribution has shifted from the reference baseline (via PSI). |
| **S** | Structural integrity | [0, 1] | Internal consistency of the evidence bundle; low values indicate tampering or corruption. |
| **I** | Interpretative coherence | [0, 1] | Semiotic alignment of the artifact against expected communicative codes; deviations suggest 逻辑断裂 (logical fracture). |
| **λ** | Drift sensitivity | ≥ 0 | Adaptive weight that controls how strongly drift amplifies risk. |
| **γ** | Integrity sensitivity | ≥ 0 | Adaptive weight governing the penalty for low structural integrity. |
| **ε** | Abstention threshold | ≥ 0 | Uncertainty boundary; if confidence is below this level, the system issues **ABSTAIN** rather than guessing. |
| **ω** | Coherence weight | ≥ 0 | Weight for interpretative penalties in the risk product. |

| Verdict | Trigger | Interpretation |
|---|---|---|
| **ACCEPT** | Risk below threshold, P near 0 | Evidence satisfies all bounded risk criteria; the artifact is treated as authentic. |
| **REJECT** | Risk above threshold, P high | The formal risk bound is breached; fabrication is indicated. |
| **ABSTAIN** | ε-level uncertainty | The system refuses to decide because confidence is insufficient, avoiding false positives and false negatives. |

| Function | Purpose |
|---|---|
| `compute_risk()` | Evaluates the collective risk formula using **deterministic integer-scaled arithmetic** (`Decimal`), never floating-point. |
| `decide()` | Generates a complete **DecisionTrace**—an immutable record of the verdict, parameters, and reasoning chain. |
| `stabilize()` | Damps proposed updates to λ, γ, and ε using momentum; rejects volatile spikes. |
| `update_from_window()` | Recalibrates parameters from a sliding window of historical false-positive and false-negative records. |
| `record_decision()` | Archives ground-truth feedback (`FABRICATED`, `AUTHENTIC`, or `None`) for future adaptation. |
| `compute_psi()` | Calculates the Population Stability Index between a reference distribution and the current one. |
| `psi_to_drift_score()` | Normalizes raw PSI to the [0, 1] interval required by the risk function. |
| `to_system_state()` / `from_policy_spec()` | Exports or reconstructs the governance state to/from a sealed forensic bundle. |

### Glossary

- **Deterministic integer arithmetic**: A calculation method that uses integer significands stored at a fixed scale (here, via `Decimal`), guaranteeing bit-exact reproducibility across CPU architectures. Floating-point (IEEE-754) is explicitly excluded.
- **Drift**: A gradual or abrupt change in the statistical distribution of evidence compared to a validated baseline.
- **Governance layer**: The architectural stratum that translates model outputs into accountable decisions, enforcing isolation from audit and action layers.
- **Isolation rule**: The architectural policy that permits this layer to read only from `models/` and `engine/`, never from `audit/` or `action/`, preventing circular dependencies.
- **Momentum**: A stabilizing term borrowed from control theory that preserves a fraction of previous parameter values to smooth out updates.
- **Parameter damping**: A suppressive factor that attenuates oscillations in adaptive feedback loops.
- **Posterior probability (P)**: In Bayesian terms, the updated probability of a hypothesis (fabrication) after observing evidence.
- **PSI (Population Stability Index)**: A symmetric divergence statistic used to quantify distributional shift; values above 0.2 indicate severe drift.
- **Risk bounding**: The practice of enforcing upper limits on acceptable risk, ensuring decisions remain within scientifically defensible margins.
- **Traceability**: The property of a decision being fully reconstructible from its recorded parameters, inputs, and code version.

> 【Scientific Note】
> This module occasionally references semiotic frameworks—**Charles Sanders Peirce** (theory of signs and abductive inference), **Umberto Eco** (interpretative codes and the limits of overinterpretation), and **H.P. Grice** (cooperative maxims of communication). These are **not mystical concepts**. They are formal models of how intelligent agents derive meaning from signals. Consider a laboratory spectrometer: it uses Peircean inference rules to classify wavelengths, Eco-codes (calibration tables) to map signals to chemical species, and Gricean expectations (that a pure sample will yield cooperative, non-contradictory peaks) to flag contamination. When this module evaluates an **interpretative coherence** score or detects a **logical fracture**, it is performing an analogous mechanistic reading of forensic artifacts. The terminology is philosophical, but the operation is strictly deterministic signal processing.

ESPAÑOL:

## ESPAÑOL

### ¿Qué es este módulo?
Este módulo, `risk_bounded_layer.py`, constituye la **Capa de Gobernanza (Capa 3)** del VIGÍA Forensic Suite. Su función es actuar como árbitro formal entre la inferencia estadística y la acción científico-jurídica. Recibe salidas numéricas de modelos forenses—por ejemplo, la probabilidad de que un artefacto digital haya sido fabricado—y las convierte en uno de tres veredictos deterministas: **ACCEPT**, **REJECT** o **ABSTAIN**.

Esencialmente, esta capa no utiliza aprendizaje automático opaco. Se basa en una fórmula de riesgo transparente, acordada colectivamente, y en control por retroalimentación adaptativa. Todos los cálculos se ejecutan con **aritmética determinista de enteros escalados** (mediante el tipo `Decimal`), garantizando que la misma evidencia produzca exactamente el mismo resultado en una estación Intel x86, un servidor ARM o una placa RISC-V. No existe indeterminismo de punto flotante dependiente del hardware.

### Conceptos Clave

(Similar tables, translated)

| Componente | Rol | Descripción en lenguaje sencillo |
|---|---|---|
| **RiskBoundedDecisionLayer** | Motor de decisión | Calcula la puntuación de riesgo total y emite un veredicto formal. |
| **SelfAdaptiveRiskPolicy** | Unidad de calibración | Ajusta los parámetros de sensibilidad (λ, γ, ε) a partir de un historial de errores. |
| **PolicyStabilityController** | Amortiguador de oscilación | Aplica momento (momentum) y amortiguación a las actualizaciones de parámetros para evitar oscilaciones erráticas. |

| Símbolo | Nombre | Rango | Significado |
|---|---|---|---|
| **P** | Probabilidad posterior | [0, 1] | Probabilidad de que un artefacto forense esté fabricado, dada la evidencia observada. |
| **D** | Puntuación de deriva | [0, 1] | Medida normalizada de cuánto se ha desplazado la distribución de la evidencia respecto a la línea base (vía PSI). |
| **S** | Integridad estructural | [0, 1] | Consistencia interna del paquete de evidencia; valores bajos indican manipulación o corrupción. |
| **I** | Coherencia interpretativa | [0, 1] | Alineación semiótica del artefacto respecto a los códigos comunicativos esperados; las desviaciones sugieren una ruptura lógica. |
| **λ** | Sensibilidad a la deriva | ≥ 0 | Peso adaptativo que controla cuánto amplifica la deriva el riesgo total. |
| **γ** | Sensibilidad a la integridad | ≥ 0 | Peso adaptativo que gobierna la penalización por baja integridad estructural. |
| **ε** | Umbral de abstención | ≥ 0 | Frontera de incertidumbre; si la confianza está por debajo, el sistema emite **ABSTAIN**. |
| **ω** | Peso de coherencia | ≥ 0 | Peso de las penalizaciones interpretativas dentro del producto de riesgo. |

| Veredicto | Disparador | Interpretación |
|---|---|---|
| **ACCEPT** | Riesgo inferior al umbral, P cercano a 0 | La evidencia satisface todos los criterios de riesgo acotado; el artefacto se trata como auténtico. |
| **REJECT** | Riesgo superior al umbral, P alto | Se viola el límite formal de riesgo; se indica fabricación. |
| **ABSTAIN** | Incertidumbre nivel ε | El sistema se niega a decidir porque la confianza es insuficiente, evitando falsos positivos y negativos. |

| Función | Propósito |
|---|---|
| `compute_risk()` | Evalúa la fórmula colectiva de riesgo usando **aritmética determinista de enteros escalados** (`Decimal`), nunca punto flotante. |
| `decide()` | Genera una **DecisionTrace** completa—registro inmutable del veredicto, parámetros y cadena de razonamiento. |
| `stabilize()` | Amortigua las actualizaciones propuestas de λ, γ y ε mediante momentum; rechaza picos volátiles. |
| `update_from_window()` | Recalibra parámetros a partir de una ventana deslizante de registros históricos de falsos positivos y falsos negativos. |
| `record_decision()` | Archiva retroalimentación de verdad de campo (`FABRICATED`, `AUTHENTIC` o `None`) para adaptación futura. |
| `compute_psi()` | Calcula el Population Stability Index entre una distribución de referencia y la actual. |
| `psi_to_drift_score()` | Normaliza el PSI bruto al intervalo [0, 1] requerido por la función de riesgo. |
| `to_system_state()` / `from_policy_spec()` | Exporta o reconstruye el estado de gobernanza hacia/desde un paquete forense sellado. |

### Glosario

- **Aritmética determinista de enteros**: Método de cálculo que utiliza significandos enteros almacenados a escala fija (aquí, vía `Decimal`), garantizando reproducibilidad bit-a-bit entre arquitecturas de CPU. Se excluye explícitamente el punto flotante (IEEE-754).
- **Deriva (drift)**: Cambio gradual o abrupto en la distribución estadística de la evidencia respecto a una línea base validada.
- **Capa de gobernanza**: Estrato arquitectónico que traduce las salidas de modelos en decisiones responsables, imponiendo aislamiento de las capas de auditoría y acción.
- **Regla de aislamiento**: Política arquitectónica que permite a esta capa leer únicamente de `models/` y `engine/`, nunca de `audit/` ni `action/`, evitando dependencias circulares.
- **Momento (momentum)**: Término estabilizador tomado de la teoría de control que preserva una fracción de los valores paramétricos previos para suavizar las actualizaciones.
- **Amortiguación de parámetros**: Factor supresor que atenúa las oscilaciones en los lazos de retroalimentación adaptativa.
- **Probabilidad posterior (P)**: En términos bayesianos, la probabilidad actualizada de una hipótesis (fabricación) tras observar la evidencia.
- **PSI (Population Stability Index)**: Estadístico de divergencia simétrica para cuantificar el desplazamiento distribucional; valores superiores a 0.2 indican deriva severa.
- **Acotamiento de riesgo**: Práctica de imponer límites superiores al riesgo aceptable, asegurando que las decisiones permanezcan dentro de márgenes científicamente defendibles.
- **Trazabilidad**: Propiedad de una decisión de ser completamente reconstruible a partir de sus parámetros registrados, entradas y versión de código.

> 【Nota Científica】
> Este módulo hace referencia ocasional a marcos semióticos formales: **Charles Sanders Peirce** (teoría de los signos e inferencia abductiva), **Umberto Eco** (códigos interpretativos y límites de la sobreinterpretación) y **H.P. Grice** (máximas cooperativas de la comunicación). Estos **no son conceptos místicos**. Son modelos formales de cómo los agentes inteligentes extraen significado a partir de señales. Considere un espectrómetro de laboratorio: utiliza reglas de inferencia peirceanas para clasificar longitudes de onda, códigos ecoanos (tablas de calibración) para mapear señales a especies químicas, y expectativas griceanas (de que una muestra pura producirá picos cooperativos y no contradictorios) para señalar contaminación. Cuando este módulo evalúa una puntuación de **coherencia interpretativa** o detecta una **fractura lógica**, está realizando una lectura mecanicista análoga de artefactos forenses. La terminología es filosófica, pero la operación es un procesamiento estrictamente determinista de señales.

РУССКИЙ:

## РУССКИЙ

### Что это за модуль?
Данный модуль, `risk_bounded_layer.py`, представляет собой **Уровень управления (Уровень 3)** пакета VIGÍA Forensic Suite. Его назначение — выступать формальным арбитром между статистическим выводом и научно-правовым действием. Он принимает числовые результаты от судебно-медицинских моделей — например, вероятность того, что цифровой артефакт подделан, — и преобразует их в один из трёх детерминированных вердиктов: **ACCEPT**, **REJECT** или **ABSTAIN**.

Ключевой момент: этот уровень не использует непрозрачное машинное обучение. Вместо этого он опирается на прозрачную, коллективно согласованную функцию риска и адаптивное управление с обратной связью. Все вычисления выполняются с помощью **детерминированной целочисленной арифметики с фиксированным масштабом** (тип `Decimal`), что гарантирует: одни и те же доказательства дадут абсолютно идентичный результат на рабочей станции Intel x86, сервере ARM или встроенной плате RISC-V. Отсутствует какая-либо зависимость от аппаратной недетерминированности чисел с плавающей запятой.

### Ключевые понятия

| Компонент | Роль | Описание простым языком |
|---|---|---|
| **RiskBoundedDecisionLayer** | Движок принятия решений | Вычисляет общий показатель риска и выносит формальный вердикт. |
| **SelfAdaptiveRiskPolicy** | Блок калибровки | Корректирует параметры чувствительности (λ, γ, ε) на основе истории прошлых ошибок. |
| **PolicyStabilityController** | Демпфер колебаний | Применяет момент инерции (momentum) и демпфирование к обновлениям параметров, предотвращая хаотичные скачки. |

| Символ | Название | Диапазон | Значение |
|---|---|---|---|
| **P** | Апостериорная вероятность | [0, 1] | Вероятность того, что судебный артефакт подделан, при имеющихся доказательствах. |
| **D** | Оценка дрифта | [0, 1] | Нормализованная мера смещения распределения текущих доказательств относительно базового (через PSI). |
| **S** | Структурная целостность | [0, 1] | Внутренняя непротиворечивость пакета доказательств; низкие значения указывают на подделку или повреждение. |
| **I** | Интерпретационная когерентность | [0, 1] | Семиотическое соответствие артефакта ожидаемым коммуникативным кодам; отклонения указывают на логический разрыв. |
| **λ** | Чувствительность к дрифту | ≥ 0 | Адаптивный вес, контролирующий усиление риска за счёт дрифта. |
| **γ** | Чувствительность к целостности | ≥ 0 | Адаптивный вес, определяющий штраф за низкую структурную целостность. |
| **ε** | Порог воздержания | ≥ 0 | Граница неопределённости; при недостаточной уверенности система выдаёт **ABSTAIN**. |
| **ω** | Вес когерентности | ≥ 0 | Вес интерпретационных штрафов в произведении риска. |

| Вердикт | Условие | Научная интерпретация |
|---|---|---|
| **ACCEPT** | Риск ниже порога, P близка к 0 | Доказательства удовлетворяют критериям ограниченного риска; артефакт считается подлинным. |
| **REJECT** | Риск выше порога, P высокая | Превышены формальные границы риска; имеются сильные признаки подделки. |
| **ABSTAIN** | Неопределённость уровня ε | Система отказывается от решения из-за недостаточной уверенности, избегая ложноположительных и ложноотрицательных результатов. |

| Функция | Назначение |
|---|---|
| `compute_risk()` | Вычисляет коллективно согласованную функцию риска с помощью **детерминированной целочисленной арифметики с фиксированным масштабом** (`Decimal`), без использования чисел с плавающей запятой. |
| `decide()` | Генерирует полную **DecisionTrace** — неизменяемую запись вердикта, параметров и цепочки рассуждений. |
| `stabilize()` | Демпфирует предлагаемые обновления λ, γ и ε с помощью момента инерции; отклоняет волатильные всплески. |
| `update_from_window()` | Перекалибрует параметры по скользящему окну исторических ошибок (ложные срабаты
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
