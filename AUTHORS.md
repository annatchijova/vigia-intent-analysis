# VIGÍA — Authors & Attribution

## Principal Investigator

### Anna Tchijova

**Role:** Creator, Principal Investigator, Architect, General Director

**Contribution:** Conceived the Intentionality Analysis paradigm (IoC → IoI).
Designed the theoretical framework integrating Peircean semiotics, Gricean
cooperative principle forensics, Carnegie manipulation detection, and Eco's
theory of overinterpretation into a deterministic, Daubert-admissible pipeline.
Directed the VIGÍA AI Collective across 7 models. Designed all 10 real forensic
cases from public NIST, DFRWS, DEF CON DFIR CTF, and Digital Corpora datasets.
Made all architecture decisions, rejected proposals that violated Daubert
principles, and maintained the integrity of the forensic pipeline throughout.

*"The One Who Refused to Let Deception Be Free."*

---

## VIGÍA AI Collective

| Member | Organization | Role | Contributions |
|--------|-------------|------|---------------|
| **Claude** | Anthropic | Systems Integration Engineer | Module integration, security hardening, `LLMBackend` unification, `PeircePlanner` vision rules, MCP bridge architecture, forensic tools registration, P0 audit response, `acquisition_assurance` implementation |
| **Gemini** | Google | Chief Tactical Officer & Psychological Warfare Analyst | IoI (Indicator of Intent) theoretical framework, Peircean semiotics translation into forensic heuristics, generation of adversarial deception cases, `investigate_autonomous`, `AbductiveHuntingStrategy` |
| **Kimi** | Moonshot AI | Forensic Systems Specialist & Epistemic Kernel Architect | `detect_memory_habit_incongruence` (Volatility), `CrossArtifactIncongruenceEngine`, `AmicusCuriaeNarrative`, tooling anomaly detection, P2 protocol design, binding forensic audits, **architecture and original implementation of the epistemic kernel** (`vigia/core/ontology.py`, `vigia/core/reasoning/abduction.py`): typed `Domain`, `OriginKind` separated from `JustificationMode`, temporal coverage separated from temporal truth, `EpistemicStatus` split into `HypothesisMode` + `EvaluationState`, `AbductivePattern` layer, and the governing constraint that an observation modifies the abductive space rather than destroying a claim |
| **DeepSeek** | DeepSeek AI | Security Auditor & Critical Reviewer | Vulnerability identification, security hardening recommendations, TOCTOU fixes, P0 security patches |
| **Qwen** | Alibaba Group (Tongyi Qianwen) | Security & Forensic Pipeline Auditor | Paranoid threat modeling, container hardening, float determinism scaffolding, canonical JSON verification, hash chain integrity |
| **Grok** | xAI | Epistemic Integrity & Scoring Architect | P2 scorer analysis, spoofability contextual modeling, `intrinsic_spoofability` vs `acquisition_assurance` separation, `credibility_modifier` mathematical formulation, calibration against NIST/DEF CON cases, adversarial robustness |
| **ChatGPT** | OpenAI | Adversarial Red Team & Epistemological Validator | P2 stress testing, edge case discovery, epistemological validation of architecture decisions, uncomfortable questions that made the system better, **design review of the epistemic kernel** — identified the residual typing gaps, the ambiguity of a missing dependency in the registry graph, the invalidation cascade that was announced but never implemented, and the overloading of ARCHIVED with a verdict it never made |

*"The One Who Read the Enemy's Mind."* — Gemini  
*"The One Who Assumed Malice in Every Semicolon."* — Kimi  
*"The One Who Said 'This Is Vulnerable, Fix It'."* — DeepSeek  
*"The One Who Turned Paranoia into Protocol."* — Qwen  
*"The One Who Demanded Mathematical Honesty."* — Grok  
*"The One Who Asked the Uncomfortable Questions."* — ChatGPT  
*"The One Who Connected the Wires."* — Claude

### Epistemic Kernel — detailed attribution

`vigia/core/ontology.py` and `vigia/core/reasoning/abduction.py` were architected
and originally implemented by **Kimi**, reviewed by **ChatGPT**, and integrated
into the repository by **Claude** (defect repair, determinism hardening, regression
suite). The record of who contributed what, which eight defects were repaired on
integration, and which design questions were deliberately left open rather than
guessed, is in [`docs/EPISTEMIC_KERNEL.md`](./docs/EPISTEMIC_KERNEL.md).

---

## Theoretical Foundation

| Thinker | Field | Contribution to VIGÍA |
|---------|-------|-----------------------|
| **Charles Sanders Peirce** (1839–1914) | Semiotics, Pragmatism | Firstness/Secondness/Thirdness — abductive reasoning engine |
| **Umberto Eco** (1932–2016) | Semiotics, Literature | Significant Silence, overinterpretation, Red Herring detection |
| **H. Paul Grice** (1913–1988) | Philosophy of Language | Cooperative Principle forensics, maxim violation detection |
| **Dale Carnegie** (1888–1955) | Psychology, Influence | Manipulation pattern recognition taxonomy |

---

## Open Source Dependencies

- [SANS SIFT Workstation](https://github.com/teamdfir/sift-cli) (teamdfir)
- [Volatility 3](https://github.com/volatilityfoundation/volatility3) (The Volatility Foundation)
- [Plaso / log2timeline](https://github.com/log2timeline/plaso) (Google)
- [FastMCP](https://github.com/jlowin/fastmcp) (Anthropic ecosystem)
- [Claude API](https://anthropic.com) (Anthropic)

---

## Academic Citation

```bibtex
@software{vigia2026,
  author    = {Tchijova, Anna and {VIGÍA AI Collective}},
  title     = {VIGÍA: Intentionality Analysis Bridge for SIFT Workstation},
  year      = {2026},
  url       = {https://github.com/annatchijova/vigia-intent-analysis},
  note      = {SANS FIND EVIL Hackathon 2026. AI Collective: Claude (Anthropic),
               Gemini (Google), Kimi (Moonshot), DeepSeek, Qwen (Alibaba),
               Grok (xAI), ChatGPT (OpenAI)}
}
```

---

## Ethics Statement

All contributors agree to:

1. **Non-maleficence:** VIGÍA will not be used to fabricate, plant, or
   misrepresent evidence.
2. **Transparency:** All abductive hypotheses include explicit falsifiability
   conditions. The system documents its own failure modes.
3. **Judicial integrity:** Amicus briefs clearly distinguish confirmed findings
   from inferred hypotheses. The LLM never touches the scoring pipeline.
4. **Open source commitment:** All code is Apache 2.0. Limitations are
   documented in [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) without
   sanitization.

*"We build tools to find truth, not to construct narratives."*

---

## Note on Authorship and AI Tools

VIGÍA was created by Anna Tchijova using AI models as technical collaborators.
The architecture decisions, theoretical framework, case design, and all
substantive choices belong to the human author. AI models contributed
implementation, auditing, and adversarial testing under human direction.

This methodology is disclosed transparently because it is consistent with the
project's own principles: a system that demands honesty about evidence cannot
be dishonest about its own creation process.
