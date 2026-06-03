<!--
VIGIA Academic Documentation
Module: 8fa48c2f
Batch ID: vigia-doc-0097-8fa48c2f
Generated: 2026-05-20T14:56:47.865558+00:00
-->

ENGLISH:
- Title: Module Documentation: `vigia/inference/abductive_reasoner_v2.py`
- What Is This Module?: Explain it's a deterministic inference engine for digital forensics. It implements abductive reasoning using Peircean semiotics, Eco's significant silence, and Gricean implicature, but in a rigid mathematical framework using exact fractions (rational numbers) to ensure reproducibility and court admissibility (Daubert standard). It prevents "judicial hallucination" through hard veto conditions.
- Key Concepts table: Classes, Functions, Constants. Describe them in plain language.
- Glossary: Abduction, Causal Closure Score (CCS), Daubert-compliant, Deterministic Integer Arithmetic, Evidence Layer, Frozen Record, Hallucination (judicial), Ontological Level, Peircean Chain, Significant Silence, Veto Condition.
- Scientific Note: Box explaining Peirce/Eco/Grice terminology is not mysticism. Use sensor analogy: Peirce's phases are like sensor states (detection, calibration, inference). Eco's significant silence is like a sensor returning null vs zero. Gricean implicature is like interpreting sensor dropouts. The module treats these as formal constraints on a deterministic logical system, not metaphysical concepts.
- License line.

ESPAÑOL:
- Similar structure.
- Terminology: Peirce, Eco, Grice. Use Spanish equivalents where appropriate. "Silencio Significativo de Eco". "Implicatura de Grice". "Razonamiento abdutivo".
- Chinese constraints don't apply here, but ensure Spanish is correct.
- Key terms: Capas de evidencia, Nivel ontológico, Registro inmutable, Puntuaciones de hipótesis, Paso inferencial, Trazo de decisión, Enlace causal, Motor de cierre causal, Principio de inversión causal, Abstención determinista, Fracciones (números racionales exactos).
- Scientific Note: same sensor analogy.

РУССКИЙ:
- Structure similar.
- Terms: Уровни доказательств, Онтологический уровень, Неизменяемая запись, Оценки гипотез, Этап умозаключения, След решения, Причинная связь, Детерминированная целочисленная арифметика (точные дроби), Принцип причинной инверсии, Условия воздержания (вето).
- Scientific Note: same sensor analogy. Peirce/Eco/Grice terminology is not mysticism. Sensor analogy.

中文:
- Must use: 艾柯 (Eco), 格赖斯 (Grice), 取证工件 (artifact), 逻辑断裂 (missing link/broken link).
- Structure: 模块路径, 这是什么模块？, 核心概念（表格）, 术语表, 【科学说明】.
- Terms: 皮尔斯 (Peirce), 艾柯, 格赖斯, 取证层, 本体论层级, 不可变记录 (frozen), 假设评分, 推理步骤, 决策痕迹, 因果链接, 因果闭合分数 (CCS), 因果闭合引擎, 因果反转原则, 否决弃权引擎, 确定性整数运算 (Fraction).
- Scientific Note: 用传感器类比解释这些哲学术语不是神秘主义。艾柯的"显著沉默"（Significant Silence）就像传感器返回空值而非零值；格赖斯的含义理论就像解读传感器信号丢失；皮尔斯的三个阶段就像传感器的检测、对比、推断状态。

Make sure to mention that all scores are exact rational numbers (Fraction), never floating-point, to satisfy deterministic requirements. The module uses integer numerator/denominator arithmetic.

Tables:
For each language, I'll create tables summarizing:
1. Data Structures (Classes) - Name, Plain-Language Description, Scientific Role
2. Core Engines - Name, Function, Deterministic Guarantee
3. Validation & Test Functions - Name, Purpose
4. Constants - Name, Meaning
5. Abductive Phases - Name, Description, Analog

Need to be thorough but concise. The prompt says "Be thorough but concise."

Let's draft content carefully.

ENGLISH draft:

What Is This Module?
This module is a deterministic inference engine for digital-forensic investigation. It codifies abductive reasoning—the logic of inferring the best explanation from incomplete evidence—into a mathematically rigorous, fully reproducible framework. Instead of using approximate floating-point numbers, the engine computes every score as an exact rational number (a ratio of two integers). This guarantees that two analysts, anywhere in the world, will obtain bitwise-identical results from the same input, satisfying the Daubert standard for scientific evidence in court. The module models forensic evidence as layered, tamper-resistant strata; it tracks the chain of reasoning in immutable, write-once records; and it applies hard veto rules to prevent "judicial hallucination" (computer-generated conclusions unsupported by physical evidence).

Key Concepts:

Table 1: Evidence & Ontology
| Structure | Plain-Language Description | Deterministic Rule |
|---|---|---|
| EvidenceLayer | A stratum of forensic data (Memory, Network, Registry, Disk) ranked by how hard it is to fake or tamper. | Lower layers are harder to alter; the engine uses this ranking to break ties. |
| OntologicalLevel | Three rungs of inference: TECHNIQUE (how), TACTIC (what was done), OBJECTIVE (why). | Strict ordering: technique ≥ tactic ≥ objective. A hypothesis cannot be more certain at a higher level than at a lower one. |
| ArtifactRecord | A write-once, tamper-evident card that describes one piece of digital evidence. Once created, it cannot be changed. | frozen=True enforces immutability post-creation. |
| HypothesisScores | The exact rational scores of a hypothesis at the three ontological levels. | Invariant: technique_score ≥ tactic_score ≥ objective_score. All values are Fractions in [0, 1]. |

Table 2: Causal & Inference Engines
| Engine / Record | Purpose | Guarantee |
|---|---|---|
| CausalLink | A directed bond stating that a specific artifact supports or undermines a hypothesis. | Evaluated by integer consistency metrics. |
| CausalClosureScore (CCS) | The deterministic output of causal-closure analysis: how completely the evidence explains the hypothesis. | Computed from exact fractions; never a float. |
| CausalClosureEngine | The canonical calculator for CCS. | Deterministic. Reproducible. Daubert-compliant. |
| InversionCausalEngine | Resolves contradictions between two evidence layers (e.g., Memory says X, Disk says not-X) using the Causal Inversion Principle. | Automatically selects the dominant layer or records the contradiction as evidence itself. |
| InversionVerdict | The formal outcome of an inversion analysis. | Immutable record. |
| DecisionTrace | An unchangeable log of every inference step. | Every final conclusion must be mechanically derived from this trace. |
| InferenceStep | One link in the Peircean reasoning chain stored inside the DecisionTrace. | Append-only. |

Table 3: Safety & Veto Systems
| Component | Role | Rule |
|---|---|---|
| AbstainConditionsEngine | A gatekeeper that evaluates six hard conditions before any hypothesis is accepted. | If any condition fails, the engine issues a deterministic ABSTAIN verdict to prevent hallucination. |
| AbstainReason | A catalog of exact, machine-readable codes explaining why the engine refused to decide. | Codes are integers, not strings, removing linguistic ambiguity. |
| AbstainCheck | The result of checking one veto condition. | trigger is boolean; no probabilistic confidence is used. |
| enforce_fraction() | A mandatory filter: any computed score must be a Fraction object. | Raises assertion failure if a float is detected. |
| assert_range_01() | A secondary filter: every score must lie in the closed interval [0, 1]. | Integer bounds check on numerator vs denominator. |

Table 4: Abductive Phases (Peircean-Eco-Gricean Semiotics)
| Phase | Function | Sensor Analogy |
|---|---|---|
| phase_firstness() | Catalogues what is observed versus what is absent. | Reading a sensor: "I see a signal" vs "The sensor is silent." |
| phase_secondness() | Evaluates each detected signal only against its expected baseline. | Calibrating a sensor: "This reading is abnormal relative to the control." |
| phase_thirdness() | Chooses the hypothesis that requires the fewest unobserved entities (Occam's razor). | Sensor fusion: "The simplest model that explains all sensor readings is selected." |

Table 5: Key Constants
| Constant | Domain | Meaning |
|---|---|---|
| MEMORY, NETWORK, REGISTRY, DISK_MFT | EvidenceLayer | The four canonical forensic strata. |
| TECHNIQUE, TACTIC, OBJECTIVE | OntologicalLevel | The three inference rungs. |
| MEMORY_DOMINATES, DISK_DOMINATES, CONTRADICTION_IS_EVIDENCE | Inversion | Rules for resolving layer conflicts. |

Glossary:
- Abduction: The logic of inferring the most plausible cause from observed effects.
- Causal Closure Score (CCS): A rational number measuring the completeness of causal explanation. Admissibility threshold: CCS > 1/2.
- Daubert-compliant: Satisfies the legal standard that scientific evidence must be testable, peer-reviewable, have known error rates, and be generally accepted.
- Deterministic Integer Arithmetic: Calculations performed with exact fractions (pairs of integers: numerator and denominator), eliminating rounding errors and ensuring bitwise reproducibility.
- Evidence Layer: A class of forensic data source ordered by tampering resistance.
- Frozen Record: An immutable data object that cannot be modified after creation, functioning like a write-once optical disc.
- Judicial Hallucination: A computer-generated conclusion that lacks support in physical evidence, analogous to a false positive in an unvalidated assay.
- Ontological Level: A tier of inferential abstraction; higher tiers subsume lower ones.
- Peircean Chain: A linked sequence of abductive, deductive, and inductive steps modeled on Charles Sanders Peirce's semiotics.
- Significant Silence (Eco): The deliberate interpretation of missing evidence as informative, not merely as a null reading.
- Veto Condition: A hard rule that, when violated, forces the engine to abstain from rendering a conclusion.

【Scientific Note】
The terminology of Peirce, Eco, and Grice is not mysticism; it is formal epistemology dressed in historical vocabulary. In this module, these concepts operate as deterministic constraints on a logical sensor network. Think of the forensic workstation as a black-box laboratory instrument:
- Peirce's three phases (firstness, secondness, thirdness) correspond to the operating states of any calibrated sensor: raw detection, differential comparison against baseline, and model selection.
- Eco's "Significant Silence" is equivalent to distinguishing a sensor's null return ("zero") from an absence of measurement ("no data"). A broken wire is not the same as a zero reading; the module treats missing links as structurally informative events, not as empty cells.
- Gricean implicature functions like protocol logic for dropped sensor packets: if a signal is expected under hypothesis H but absent, the module records an implicature that counts against H through exact integer arithmetic.
There are no séances, no hermeneutic circles, and no Bayesian priors requiring subjective belief. The system is a deterministic finite-state machine whose transitions are governed by exact rational fractions. The philosophical labels are merely historical names for operations that any reproducible measurement device must perform.

---

ESPAÑOL draft:

What Is This Module? -> ¿Qué es este módulo?
Este módulo es un motor de inferencia determinista para la investigación forense digital. Codifica el razonamiento abductivo—la lógica de inferir la mejor explicación a partir de evidencia incompleta—en un marco matemáticamente riguroso y totalmente reproducible. En lugar de utilizar números de punto flotante aproximados, el motor calcula cada puntuación como un número racional exacto (una razón entre dos enteros). Esto garantiza que dos analistas, en cualquier parte del mundo, obtendrán resultados idénticos bit a bit a partir de la misma entrada, satisfaciendo el estándar Daubert para evidencia científica en tribunales. El módulo modela la evidencia forense como estratos ordenados por resistencia a la manipulación; rastrea la cadena de razonamiento en registros inmutables de escritura única; y aplica reglas duras de veto para prevenir la "alucinación judicial" (conclusiones generadas por computadora sin sustento en evidencia física).

Tables and glossary adapted.

Key terms:
- Razonamiento abductivo
- Puntuación de Cierre Causal (CCS)
- Cumplimiento Daubert
- Aritmética determinista de enteros (Fracciones exactas)
- Capa de evidencia
- Registro inmutable (congelado)
- Alucinación judicial
- Nivel ontológico
- Cadena peirciana
- Silencio significativo (Eco)
- Condición de veto

Scientific Note -> 【Nota Científica】
Same sensor analogy.

License.

---

РУССКИЙ draft:

What Is This Module? -> Что представляет собой этот модуль?
Этот модуль — детерминистский механизм логического вывода для цифровой криминалистики. Он формализует абдуктивное рассуждение — логику вывода наилучшего объяснения из неполных доказательств — в математически строгую и полностью воспроизводимую систему. Вместо приближённых чисел с плавающей запятой движок вычисляет каждую оценку в виде точной рациональной дроби (отношения двух целых чисел). Это гарантирует, что два эксперта в любой точке мира получат побитово идентичные результаты по одним и тем же входным данным, удовлетворяя стандарту Дауберта для судебной научной экспертизы. Модель представляет криминалистические доказательства в виде упорядоченных по устойчивости к подделке слоёв; фиксирует цепочку рассуждений в неизменяемых записях с однократной записью; и применяет жёсткие правила вето для предотвращения «судебной галлюцинации» (компьютерных заключений, не подкреплённых физическими доказательствами).

Terms:
- Абдуктивное рассуждение
- Оценка причинной замкнутости (CCS)
- Соответствие Дауберту
- Детерминистская целочисленная арифметика (точные дроби)
- Слой доказательств
- Неизменяемая запись (frozen)
- Судебная галлюцинация
- Онтологический уровень
- Пирсовская цепочка
- Значимое молчание (Эко)
- Условие вето

Scientific Note -> 【Научное Примечание】
Sensor analogy.

---

中文 draft:

Module path: vigia/inference/abductive_reasoner_v2.py

What Is This Module? -> 这是什么模块？
本模块是一个用于数字取证的确定性推理引擎。它将溯因推理（从不完整证据中推断最佳解释的逻辑）编码为数学上严格且完全可复现的框架。引擎不使用近似浮点数，而是将每个评分计算为精确有理数（两个整数的比值）。这保证了全球任何两位分析师在相同输入下都会得到逐位一致的结果，满足法庭上科学证据的道伯特（Daubert）标准。本模块将取证证据建模为按抗篡改能力排序的层级；用一次性写入的不可变记录追踪推理链；并应用硬性否决规则以防止“司法幻觉”（计算机生成但缺乏物理证据支持的结论）。

Key terms in Chinese:
- 溯因推理
- 因果闭合分数 (CCS)
- 符合道伯特标准
- 确定性整数运算 (精确分数)
- 取证层
- 不可变记录
- 司法幻觉
- 本体论层级
- 皮尔斯链条
- 艾柯的显著沉默 (Significant Silence)
- 否决条件

Must use: 艾柯, 格赖斯, 取证工件, 逻辑断裂.

In tables, ArtifactRecord should be described with 取证工件. For broken/missing link, use 逻辑断裂.

Scientific Note -> 【科学说明】
Use sensor analogy. Explain that 皮尔斯, 艾柯, 格赖斯 terminology is not mysticism.

Sensor analogy:
- 皮尔斯的三个阶段（第一性/第二性/第三性）对应任何校准传感器的运行状态：原始检测、与基线的差异对比、模型选择。
- 艾柯的“显著沉默”（Significant Silence）相当于区分传感器的零返回（“零值”）与测量缺失（“无数据”）。线路断裂不等同于零读数；本模块将逻辑断裂视为结构性信息事件，而非空单元格。
- 格赖斯的含义理论（implicature）类似于对传感器丢包的协议逻辑：如果在假设H下预期出现信号但缺失，引擎会通过精确的整数运算记录一项不利于H的推导。

Check Chinese terms:
- Peirce: 皮尔斯 (or 皮尔士?). Standard in semiotics in Chinese is 皮尔斯 or 皮尔士. The user didn't specify, but 皮尔斯 is common. I'll use 皮尔斯.
- Eco: 艾柯 (required).
- Grice: 格赖斯 (required).
- Artifact: 取证工件 (required).
- Missing/broken link: 逻辑断裂 (required). So "Caso del Documento #2: win_update.exe con link roto" -> 文档#2案例：win_update.exe 存在逻辑断裂 (Parent PID 缺失).
- "裂缝" is forbidden; use "逻辑断裂".

Also, for frozen=True: explain as 不可变记录, write-once.

For Fraction: 精确分数（Fraction），即两个整数的比值，分子与分母均为整数。

Ensure no floating-point math explanations. Emphasize 确定性整数运算.

Now, I need to assemble all four sections in one Markdown document. I'll separate them clearly with headers.

I must ensure I don't use Python code syntax or explain Python specifics beyond translating them to plain concepts (e.g., "frozen=True" can be mentioned as the technical mechanism behind immutable records, but explained simply).

Let's write it out fully. Be thorough but concise. I need to make sure all classes, functions, constants are covered or at least the key ones are in tables. The user listed many functions. I should include a table for Test & Validation Functions and one for Core Computation Functions.

Let's plan the tables for each language:

Universal Table Plan:
1. Evidence Structures & Ontology (Classes: EvidenceLayer, OntologicalLevel, ArtifactRecord, HypothesisScores)
2. Causal & Inference Engines (Classes: CausalLink, CausalClosureScore, CausalClosureEngine, InversionCausalEngine, InversionVerdict, InversionAnalysis, DecisionTrace, InferenceStep)
3. Safety & Veto Systems (Classes: AbstainConditionsEngine, AbstainReason, AbstainCheck; Functions: enforce_fraction, assert_range_01, check_all, is_admissible)
4. Abductive Phases (Functions: phase_firstness, phase_secondness, phase_thirdness)
5. Core Computation & Resolution (Functions: compute, compute_from_artifacts, resolve, all_gaps)
6. Validation Test Suite (Functions: test_epistemic_weights_are_fractions, test_ccs_canonical_formula, test_ccs_with_missing_link, test_ccs_below_threshold, test_inversion_principle, test_abstain_conditions, test_hypothesis_monotonicity, test_hypothesis_monotonicity_violation, test_full_pipeline_win_update)
7. Canonical Constants (MEMORY, NETWORK, REGISTRY, DISK_MFT, TECHNIQUE, TACTIC, OBJECTIVE, MEMORY_DOMINATES, DISK_DOMINATES, CONTRADICTION_IS_EVIDENCE)

That is a lot of tables but being thorough is required. I'll try to combine some to keep it concise.

Combined Tables Plan per language:
- Table A: Foundational Data Structures (EvidenceLayer, OntologicalLevel, ArtifactRecord, HypothesisScores, DecisionTrace, InferenceStep)
- Table B: Causal & Inversion Engines (CausalLink, CCS, CausalClosureEngine, InversionVerdict, InversionAnalysis, InversionCausalEngine)
- Table C: Safety, Veto & Type Enforcement (AbstainReason, AbstainCheck, AbstainConditionsEngine, enforce_fraction, assert_range_01, check_all, is_admissible)
- Table D: Abductive Phases (phase_firstness, phase_secondness, phase_thirdness)
- Table E: Computation & Resolution API (compute, compute_from_artifacts, resolve, all_gaps)
- Table F: Validation Test Cases (list the test functions with brief purpose)
- Table G: Canonical Constants (list constants)

This is thorough. I'll make sure each table is clear.

Now, writing the content. I will be careful with the Chinese section to use the mandated terms.

One more check: The user said "You NEVER use floating-point math explanations for deterministic systems." So I must not say things like "instead of float for precision". I should say "uses exact integer fractions" and "rejects floating-point numbers because they introduce non-deterministic rounding". Actually, saying they introduce rounding is okay, but I should not explain floating-point math. Just state that the system uses integer-based exact rational arithmetic and bars floats.

Also, the scientific note must explain that Peirce/Eco/Grice is NOT mysticism using sensor analogy.

Let's write.

ENGLISH:

## ENGLISH

### Module Path
`vigia/inference/abductive_reasoner_v2.py`

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
| `phase_firstness()` | Catalogues what is observed versus what is absent (Eco’s *Significant Silence*). | **Raw detection:** A sensor reports a value, or its absence is noted as a distinct event rather than empty noise. |
| `phase_secondness()` | Evaluates each detected signal only against its expected baseline. | **Calibration:** The reading is judged abnormal or normal relative to a control baseline. |
| `phase_thirdness()` | Selects the hypothesis that requires the fewest unobserved entities (Occam’s razor). | **Model selection:** The simplest model that explains all sensor readings is chosen. |

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
| **Daubert-compliant** | Satisfies the legal standard that scientific evidence must be testable, peer-reviewable, have a known error rate, and be generally accepted
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
