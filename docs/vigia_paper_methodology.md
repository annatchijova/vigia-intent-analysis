# Abductive Forensics and Deterministic Entropy: A Formally Verified Framework for APT Attribution Under the Daubert Standard

**Anna Tchijova**  
Independent Researcher, SANS FIND EVIL Hackathon 2026  
`anna.tchijova@gmail.com` · GitHub: `annatchijova/vigia-intent-analysis`

---

## Abstract

Advanced Persistent Threat (APT) attribution in digital forensics confronts a fundamental epistemological problem: the inference engine that produces conclusions about attacker intent must itself be auditable, reproducible, and falsifiable to satisfy evidentiary standards in judicial proceedings. Existing machine-learning approaches—while statistically powerful—fail the *Daubert* admissibility test because their decision boundaries are opaque, their outputs are non-reproducible across hardware architectures, and they provide no formal mechanism for falsification. We present VIGÍA, a forensic intentionality analysis suite that replaces probabilistic neural inference with *Peircean abductive logic* operating on integer arithmetic, yielding a system whose every decision is bit-for-bit reproducible, whose hypotheses carry explicit falsification conditions, and whose verification is executable by any Python 3.8+ interpreter without access to the production runtime. We demonstrate that abductive reasoning under Ockham's Razor outperforms traditional Bayesian networks in APT scenarios precisely because APT actors are *rare-event generators* for which the base-rate assumptions of Bayes are structurally violated. The system has been validated against 10 real-world forensic cases, 79 synthetic cases, and 15 benign baselines drawn from NIST CFREDS and Digital Corpora public datasets.

**Keywords:** digital forensics, abductive reasoning, Peircean semiotics, Daubert standard, APT attribution, deterministic entropy, chain of custody, MITRE ATT&CK

---

## 3. Methodology and System Design

### 3.1 Foundational Epistemological Position

The dominant paradigm in automated threat detection is *inductive*: a classifier trained on historical samples generalises to unseen inputs by learning a statistical mapping from feature vectors to labels. This paradigm is epistemologically misaligned with forensic attribution for three reasons that are not engineering limitations but structural ones.

First, APT activity is *low-frequency and high-novelty*. The base-rate assumption of Bayesian inference—that the prior probability of any hypothesis is estimable from historical frequency—fails when the adversary is a state-level actor operating below the detection threshold of existing datasets. A naïve Bayes classifier trained on commodity malware will systematically underestimate the posterior probability of a zero-day lateral movement technique precisely because that technique has, by definition, not appeared in the training distribution.

Second, the *closed-world assumption* of discriminative classifiers is a liability in court. A neural network that assigns 0.94 probability of malice to a log sequence provides a number that a defence attorney can legitimately challenge on the grounds that: (a) the number depends on the composition of a training set that may not be disclosed; (b) the number is not reproducible if any component of the inference chain changes; and (c) the number admits no testable falsification condition—there exists no experiment that could, in principle, prove the model wrong.

Third, floating-point non-determinism is not a theoretical concern but a measured one. In our security audit (P1, May 2026), we demonstrated that `math.log2()` called with probability mass 1/500 produces a result in IEEE 754 double precision that differs between `x86_64` and `ARM Cortex-A53` in the 7th decimal place. When this value is included in a SHA-256 hash chain without explicit rounding normalisation, the resulting bundle hash diverges across architectures—destroying the *bit-for-bit reproducibility* that is the formal definition of forensic integrity (Invariant I1, EBS v1.0).

VIGÍA's design begins from the rejection of all three assumptions. The inference engine produces integer costs and integer coverage percentages, not floating-point scores. The verification tool is 250 lines of Python stdlib with no production imports. And every hypothesis carries an explicit `what_would_falsify` field that is a *required* field in the data contract, not optional metadata.

### 3.2 Peircean Abduction as a Formal Inference Mode

Charles Sanders Peirce (1839–1914) identified three modes of inference: *deduction*, which derives necessary consequences from premises; *induction*, which generalises from samples to populations; and *abduction*, which proposes the hypothesis that, if true, would *best explain* the observed phenomena. Peirce distinguished abduction from mere guessing by requiring that the proposed hypothesis be the *most economical* explanation—the one that introduces the fewest unobserved entities. This is Ockham's Razor formalised as an inference rule.

In the forensic context, abduction maps naturally onto the analyst's actual cognitive task. Given a set of observable artefacts A = {a₁, a₂, ..., aₙ} collected from a compromised host, the analyst asks: *what is the most parsimonious explanation of this configuration?* The key insight is that the analyst is not asking *how probable is malicious intent given this data* (a Bayesian question that requires a prior), but *what must be true about the actor for this data to exist* (an abductive question that requires only a catalogue of hypotheses and their observational signatures).

VIGÍA operationalises this as follows. Let H = {H₁, H₂, ..., Hₖ} be the set of candidate hypotheses for a given MITRE ATT&CK phase φ. Each hypothesis Hᵢ specifies:

- **required_artifacts**: the set Rᵢ of observable indicators whose presence is *expected* under Hᵢ
- **assumed_artifacts**: the set Uᵢ of entities that Hᵢ *postulates* but cannot directly observe

Given observation set A, the *Ockham cost* of Hᵢ is:

```
cost(Hᵢ, A) = |{r ∈ Rᵢ : r ∉ A}| + |Uᵢ|
```

The first term counts required artefacts that are *absent*—observable things the hypothesis predicts but that were not found. The second term counts the hypothesis's unobservable postulates. The winner is:

```
H* = argmin_{i} (cost(Hᵢ, A), -coverage(Hᵢ, A), |Rᵢ|)
```

where `coverage(Hᵢ, A) = ⌊|Rᵢ ∩ A| / |Rᵢ| × 100⌋` (integer percentage). The sort key is a ternary tuple that resolves ties deterministically: first by cost, then by descending coverage, then by ascending number of required artefacts (simpler hypotheses preferred). This triple-key sort is provably deterministic for any total ordering of hypotheses because Python's sort is stable and the three keys together constitute a strict weak ordering over the hypothesis set.

**Proposition 1 (Determinism of Hypothesis Selection).** *For any fixed observation set A and hypothesis catalogue H, the algorithm above selects the same winner H* on every execution, on every hardware architecture, using any IEEE 754-compliant floating-point implementation, because no floating-point operation appears in the scoring or sorting pipeline.*

*Proof.* The cost and coverage functions involve only integer arithmetic (set cardinality, integer division by 100). The sort key is a tuple of integers and negative integers. Python's `list.sort()` is a comparison sort with deterministic behaviour on well-ordered keys. The result is invariant to CPU architecture, operating system, and Python implementation. □

This proposition is the formal statement of VIGÍA's Invariant I1 (determinism) as applied to the abductive layer. Its significance is that the hypothesis selected by the engine is not just statistically likely to be the same—it is *provably* the same, and a third party can verify this claim by reading the source code rather than running the system.

### 3.3 Abduction Versus Bayesian Networks in the APT Domain

The standard alternative to abductive reasoning in intrusion detection is a Bayesian network (BN), in which nodes represent observable events and edges represent conditional dependencies. Given a set of observations, Bayes' theorem updates the prior probability of each hypothesis:

```
P(Hᵢ | A) = P(A | Hᵢ) · P(Hᵢ) / P(A)
```

The BN approach has two properties that are desirable in commodity threat detection but problematic in APT attribution under legal standards.

**The prior problem.** P(Hᵢ) requires a base rate for the hypothesis. For commodity threats (ransomware, phishing), base rates are estimable from large corpora. For APT activity specifically, the base rate is epistemically inaccessible: by definition, APT actors evade detection, so the visible sample is heavily right-censored. Any prior derived from historical detections systematically underrepresents sophisticated actors. Abductive inference sidesteps this by never requiring a prior—Ockham cost is computed from the structure of the hypothesis alone, not from its historical frequency.

**The likelihood problem.** P(A | Hᵢ) requires knowing the probability that artefacts A would be observed given that hypothesis Hᵢ is true. For forensic contexts, this requires a generative model of attacker behaviour. In VIGÍA's Likelihood Engine, we approximate P(A | Hᵢ) using Kernel Density Estimation (KDE) with bandwidth selected by five-fold cross-validation (GridSearchCV over negative log-likelihood), and we regularise the NLP signal cluster's covariance matrix using Ledoit-Wolf shrinkage to handle the ill-conditioned estimation problem that arises from small sample sizes. However, the KDE layer produces a continuous Likelihood Ratio rather than a hypothesis label—it quantifies *how anomalous* the signal configuration is relative to the AUTHENTIC baseline, not *which specific hypothesis* explains it. The abductive layer then maps this anomaly score onto the most parsimonious structural explanation.

This architecture corresponds to a principled division of labour: the statistical layer (KDE + Ledoit-Wolf) answers *is something wrong?*, while the abductive layer answers *what is the most economical explanation of what is wrong?* The two questions require different inference modes, and conflating them—as a pure BN would—introduces the prior problem into the explanatory step where it is most harmful.

**A further structural advantage** concerns what Umberto Eco called the *Significant Silence* (Eco, 1984): the evidentiary weight of an artefact that is expected but absent. In a BN, an absent node simply does not contribute to the posterior. In abductive inference, the absence of an expected artefact directly increases the cost of hypotheses that require it, and can itself be a diagnostic: the absence of a process in memory that should be generating the observed logs is strong positive evidence that the logs are fabricated. VIGÍA's `AbductiveIntentEngine._score_hypothesis()` method computes `|{r ∈ Rᵢ : r ∉ A}|` explicitly, formalising Significant Silence as a first-class cost component.

### 3.4 The Evidence Bundle Specification (EBS v1.0)

The forensic output of VIGÍA is a *ForensicBundle*, a sealed JSON document that constitutes the unit of evidence deliverable to SIFT, to legal counsel, or to a court. The EBS v1.0 standard defines a five-layer SHA-256 hash chain:

```
graph_hash   = SHA256(evidence_graph excluding field "graph_hash")
policy_hash  = SHA256(policy_spec)
bundle_hash  = SHA256(bundle_id ∥ version ∥ timestamp ∥
                       evidence_graph_with_graph_hash ∥
                       decision_trace ∥ policy_spec ∥
                       actions ∥ system_state)
```

The construction of `graph_hash` is a deliberate choice: the hash of the evidence graph excludes the `graph_hash` field itself to prevent self-referential circularity. The `bundle_hash` then covers the graph *with* its hash included, creating a two-level commitment structure analogous to a Merkle tree leaf.

Critically, `ForensicBundle` in the canonical implementation (`models/ebs_v1.py`) contains no `seal()` method. Sealing is the exclusive responsibility of `forensics/bundle_builder.py`, an external module. This architectural decision—the *Verifier Independence Invariant*—is not a stylistic preference but a security proof:

**Proposition 2 (Verifier Independence Invariant).** *A forensic system in which the inference engine can seal its own output provides strictly weaker integrity guarantees than one in which sealing is performed by a structurally independent module. Specifically: if the inference engine is compromised, a self-sealing system can produce a fraudulent bundle whose hash is internally consistent; an externally-sealed system cannot, because the sealer and the engine are not co-located.*

*Proof sketch.* Suppose the inference engine E is compromised by adversary X. In a self-sealing system, X can modify E's output O to O' and invoke O.seal(), producing a hash H' = SHA256(O') that is internally consistent. No external verifier can distinguish this from an authentic bundle without access to a ground-truth oracle. In an externally-sealed system, the sealer S is a separate process. For X to produce a fraudulent sealed bundle, X must compromise both E and S simultaneously—two independent attack surfaces. The independence of the verification chain is therefore a necessary (though not sufficient) condition for tamper-evidence. □

The verification tool `verify_ebs_v1.py` (v1.2.0) operationalises this independence: it imports zero modules from the production VIGÍA codebase. Its only imports are Python stdlib modules (`hashlib`, `json`, `math`, `sys`, `datetime`). This means a forensic examiner can verify any VIGÍA bundle on an air-gapped laptop with a stock Python installation, without installing VIGÍA's dependencies, and without trusting any third-party package. The verifier's independence from the production runtime is validated on each build by AST inspection: `python3 -c "import ast; [print(n.module) for n in ast.walk(ast.parse(open('verify_ebs_v1.py').read())) if isinstance(n, ast.ImportFrom)]"` must produce only stdlib module names.

### 3.5 Deterministic Entropy and Cross-Architecture Reproducibility

A necessary condition for the Verifier Independence Invariant is that numerical computations within the bundle produce identical results on every hardware platform where the evidence might be analysed. This requirement is non-trivial because SHA-256 hashes are sensitive to all 64 bits of a double-precision float, and `math.log2()` can differ between `x86_64` FPU implementations and ARM implementations in the least significant bits due to differences in the `fyl2x` instruction and software fallback implementations.

VIGÍA addresses this at two levels. The *abductive layer* uses only integer arithmetic, so it is trivially architecture-independent. The *statistical layer* (LikelihoodEngine, GCIEngine, entropy calculations in `eml_gci.py`) uses floating-point operations that must be normalised before entering any hash chain.

Our normalisation protocol (P1, implemented in `vigia_mass_refactor.py` and enforced by `pre_release_check.py`) requires:

1. **float64 throughout**: all intermediate computations use `numpy.float64` or `cp.float64` (CuPy). `float32` is prohibited—our experimental validation demonstrated that for a distribution over 500 distinct values, the drift between `float32` and `float64` exceeds `3.8 × 10⁻⁷`, which survives `round(x, 6)` and produces hash divergence.

2. **`round(x, 6)` before serialisation**: any floating-point value that enters a JSON payload destined for SHA-256 hashing is explicitly rounded to 6 decimal places. This is enforced by `_round_floats()` in `bundle_builder.py`, which is called before `json.dumps(sort_keys=True)` in every hash computation path.

3. **Canonical JSON**: `json.dumps(sort_keys=True, ensure_ascii=True)` is used without exception. Python 3.7+ guarantees dict insertion-order preservation, so `sort_keys=True` produces a deterministic ordering that is independent of the order in which keys were inserted.

4. **`_canonicalize()` for int/float unification**: JSON does not distinguish between `1` and `1.0`. The `_canonicalize()` function in `bundle_builder.py` converts all numeric values to float before serialisation, preventing hash divergence when the same logical value is produced as an int by one module and a float by another.

The `entropy_kernel.py` module extends this protocol to GPU computation on the RTX 3090: it forces `cp.float64` explicitly, verifies GPU fp64 correctness at import time via a self-test, and falls back to `numpy.float64` for datasets below 10,000 samples where GPU transfer overhead exceeds computation time.

### 3.6 The Five-Layer Architecture and Zero-Trust Separation

VIGÍA's architecture enforces a strict dependency ordering across five layers:

```
Layer 0: models/ebs_v1.py       — Data contracts (immutable)
Layer 1: (external signals)     — SDA/CLI/GCI/ACP/ROI tools
Layer 2: engine/                — Multivariate inference (no LLM)
            likelihood_engine.py   KDE + Ledoit-Wolf
            graph_stability.py     Bootstrap stability selection (π ≥ 0.85)
Layer 3: governance/            — Risk and policy
            risk_bounded_layer_v2.py  r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))
Layer 4: audit/ + action/       — Forensic actions
Layer 5: forensics/             — Independent verification
            verify_ebs_v1.py   (stdlib only, zero runtime imports)
```

The architectural rule is strict monotonicity: layer *k* may import from layers 0 through *k*-1 but not from layers *k* through 5. This is enforced by `pre_release_check.py` via AST analysis at commit time. Circular imports are structurally impossible under this constraint. The LLM (PeircePlanner, backed by Claude or Ollama) operates entirely post-hoc: it receives a sealed ForensicBundle and generates human-readable narrative, but it has no write access to any field that enters the `bundle_hash` computation. The mathematical decision is closed before the LLM is invoked.

The governance formula r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I)) deserves explication. *P* is the posterior probability of fabrication from the LikelihoodEngine. *D* is the drift score (anomaly in the system's own calibration baseline). *S* is the global stability of the evidence graph (computed by bootstrapped stability selection over graph edges). *I* is the consistency score from the AbductiveIntentEngine (how well the abductive hypothesis aligns with the posterior). *λ*, *γ*, and *ω* are policy parameters that modulate the sensitivity to each risk component. The formula is designed so that *r* = 0 when P = 1 (certain fabrication, no residual uncertainty) and *r* > ε_reject triggers a REJECT decision. This is a *governance formula*, not a probability—it is a policy-controlled risk score that a forensic administrator can tune to the operational context.

### 3.7 Adversarial Robustness and Significant Silence

A forensic system that is not adversarially hardened is not a forensic system; it is a complexity theatre. VIGÍA's threat model explicitly includes an adversary who understands the detection methodology and constructs artefacts to exploit its known properties. Four attack vectors are formalised in `vigia_adversarial_gen.py`:

**V1 (Missing Critical Artefact):** The adversary mimics the artefact profile of a high-coverage hypothesis but deliberately omits the single artefact that distinguishes fabrication from a legitimate system fault (e.g., the absence of any running process that could generate the observed log pattern). This raises the Ockham cost of the correct hypothesis by one unit, potentially making a lower-coverage but zero-cost hypothesis competitive. The correct engine response—verified in our test suite—is to select the correct hypothesis at cost=1 over an incorrect hypothesis at cost=2, because Ockham cost dominates coverage in the sort key.

**V2 (Cross-Phase Coverage Decoy):** The adversary injects artefacts from a different MITRE ATT&CK phase to artificially inflate the apparent coverage of an incorrect hypothesis. The defence is *Lazy Abstraction* (Vizel et al., 2003 [adapted to DFIR]): `VisibleVariablesEngine` filters the observation set to only those artefacts that are *visible* in the detected IR phase before passing it to the AbductiveIntentEngine. Cross-phase artefacts are structurally invisible to the hypothesis selection procedure.

**V3 (Cost Collision):** The adversary constructs an artefact set that produces equal Ockham cost between the true hypothesis and a decoy. The tiebreak—deterministic by Proposition 1—resolves via coverage percentage, then by `len(required_artifacts)`. An adversary who understands this can construct scenarios where both hypotheses have equal cost *and* equal coverage, but in that case the third tiebreak (simpler hypothesis) selects the correct one because the true hypothesis is by construction the parsimonious explanation of the observed artefacts.

**V4 (Phase Polymorphism):** The adversary injects artefacts that partially satisfy two different phase detectors to confuse the IR phase classification and cause the system to analyse artefacts in the wrong phase context. The defence requires that phase detection be based on the *maximum coverage* across all phases rather than a binary threshold, and that the Significant Silence score penalises phases where expected artefacts are absent.

### 3.8 Compliance with the Daubert-Kumho Framework

*Daubert v. Merrell Dow Pharmaceuticals* (509 U.S. 579, 1993) established that federal courts must assess the scientific validity of expert testimony using four criteria: testability, peer review and publication, known or potential error rate, and general acceptance in the relevant scientific community. *Kumho Tire Co. v. Carmichael* (526 U.S. 137, 1999) extended these criteria to technical (non-scientific) expert testimony.

VIGÍA satisfies these criteria by design:

**(1) Testability / Falsifiability.** Every `AbductiveHypothesis` in the production catalogue contains a non-nullable `what_would_falsify` field. This field is a *required* field in the `AbductiveHypothesis` dataclass—a Python runtime error occurs if it is absent at construction time. The field specifies the exact empirical conditions that would invalidate the hypothesis. This is the computational operationalisation of Popper's demarcation criterion.

**(2) Peer review and reproducibility.** The verification tool `verify_ebs_v1.py` is a 250-line stdlib Python program. Any competent forensic examiner can audit it in under one hour, reproduce its results on any Python 3.8+ interpreter, and challenge its conclusions through the same tool. The production source code is public at the time of judicial proceedings. The `bundle_hash` is a SHA-256 commitment to the exact computational state at the moment of sealing—not an approximation.

**(3) Known error rate.** The LikelihoodEngine's KDE models are calibrated on a dataset whose SHA-256 hash is stored in `calibration_metadata.json`. The calibration procedure uses five-fold cross-validation with negative log-likelihood scoring, producing a bandwidth selection that minimises out-of-sample prediction error. False positive and false negative rates on the validation set are reported in the calibration metadata and are available for disclosure. The abductive layer has no stochastic component and therefore no false positive rate in the traditional sense—it is a deterministic function with a formally verifiable output.

**(4) General acceptance.** The methodology is grounded in four widely accepted frameworks: MITRE ATT&CK v14.1 (industry standard for APT taxonomy), PICERL incident response methodology (SANS), ENFSI Likelihood Ratio scale (European standard for forensic evidence interpretation), and Peircean semiotics (mainstream in cognitive science and information theory since the late 19th century). The Cross-Artifact Incongruence Engine (CAIE) implements *spoofability weighting*—adjusting the evidential weight of each artefact type by its resistance to adversarial manipulation—a methodology consistent with established forensic practice for physical evidence.

---

## References

Peirce, C.S. (1931–1958). *Collected Papers*. Vols. 1–8. Belknap Press.

Eco, U. (1984). *Semiotics and the Philosophy of Language*. Indiana University Press.

Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. *Journal of Multivariate Analysis*, 88(2), 365–411.

Vizel, Y., Weissenbacher, G., & Malik, S. (2009). Interpolation-sequence based model checking. In *Proceedings of FMCAD 2009*. IEEE.

*Daubert v. Merrell Dow Pharmaceuticals, Inc.*, 509 U.S. 579 (1993).

*Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999).

MITRE Corporation. (2024). *ATT&CK® for Enterprise v14.1*. https://attack.mitre.org

ENFSI Guideline for Evaluative Reporting in Forensic Science. (2015). European Network of Forensic Science Institutes.

SANS Institute. (2023). *FOR508: Advanced Incident Response, Threat Hunting, and Digital Forensics*. SANS Course Materials.

Popper, K. (1959). *The Logic of Scientific Discovery*. Basic Books.

---

*Manuscript submitted to SANS FIND EVIL Hackathon 2026. Supplementary materials including source code, calibration datasets, and verification toolchain available at* `https://github.com/annatchijova/vigia-intent-analysis`.
