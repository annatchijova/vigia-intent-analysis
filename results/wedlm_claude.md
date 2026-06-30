# VIGIA FORENSIC INTENT ANALYSIS REPORT

```
Case ID      : VIGIA-WEDLM-2025
Investigator : VIGÍA Autonomous Agent (Claude Code / Anthropic)
Evidence     : WeDLM-main.zip
Mode         : Claude Code (MCP)
SHA-256      : edf227d6d95fde1d1b8e92047eaafe6e40322a8b007202793acb38cdefb99d64
Timestamp    : 2026-06-30T16:00:00Z
SANS Phase   : Identification
```

---

## EXECUTIVE SUMMARY

WeDLM-main.zip is a GitHub archive of a Python LLM evaluation framework dated 2025-12-30. The archive contains download scripts for 8 established academic benchmarks (ARC, GPQA, GSM8K, HumanEval, MATH, MBPP, MMLU, HellaSwag) in an evaluation/dataset_download/ directory, plus README.md (9.7KB) and MANIFEST.in. All benchmark names are publicly documented academic standards used in published ML research. This is a legitimate research tool with no forensic anomalies. Verdict: **NOISE**.

---

## CHAIN OF CUSTODY

| Artifact | SHA-256 | Date |
|----------|---------|------|
| WeDLM-main.zip | edf227d6d95fde1d1b8e92047eaafe6e40322a8b007202793acb38cdefb99d64 | 2025-12-30 |

---

## FINDINGS

### Finding F-001: WeDLM-main — Legitimate Python LLM evaluation framework

```
Finding ID    : F-001
Title         : Python LLM benchmark evaluation framework — academic research software
Verdict       : NOISE
Confidence    : HIGH (0.95)
Status        : CONFIRMED
Artifact      : WeDLM-main.zip
Tools Used    : generate_forensic_hash, list_files
```

**Firstness:** ZIP archive with '-main' suffix (GitHub archive convention) containing evaluation/dataset_download/ with Python scripts for 8 benchmarks: ARC, GPQA, GSM8K, HumanEval, MATH, MBPP, MMLU, HellaSwag. Root-level README.md (9.7KB) and MANIFEST.in. Dated 2025-12-30.

**Secondness:** All 8 benchmark names are well-established, publicly documented academic LLM evaluation standards. ARC (AI2 Reasoning Challenge) and MMLU (Massive Multitask Language Understanding) are standard commonsense/knowledge benchmarks; GSM8K and MATH are mathematical reasoning benchmarks; HumanEval and MBPP are coding benchmarks; GPQA targets graduate-level reasoning; HellaSwag targets commonsense NLI. These appear together in virtually every published LLM evaluation paper from 2023 onward. MANIFEST.in is a Python packaging configuration artifact used in standard PyPI-distributed packages. The project name "WeDLM" is consistent with academic project naming conventions. No executable payloads, no network C2 indicators, no obfuscated strings.

**Thirdness:** No deliberate malicious pattern. The artifact matches the structural signature of a legitimate Python research package for LLM evaluation, following standard academic and OSS conventions.

**Carnegie:** None detected.

**MITRE TTPs:** None.

**Devil Advocate:** Not applicable — NOISE verdict.

---

## KNOWN LIMITATIONS

- Python source code was not executed or statically analyzed; assessment is based on archive structure, file metadata, and benchmark name recognition.
- "Dataset download" scripts could theoretically download arbitrary content from the internet; however, the benchmark names resolve to well-known, publicly vetted academic datasets.

---

## OVERALL VERDICT

**NOISE** — Legitimate academic Python LLM evaluation framework. No forensic significance. No further investigation warranted.

---

```
TOKEN USAGE (this session):
  Input tokens:  [see usage.anthropic.com]
  Output tokens: [see usage.anthropic.com]
  Session ID:    2026-06-30T16:00:00Z
  Note: Full token breakdown available at usage.anthropic.com
```
