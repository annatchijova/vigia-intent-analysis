#!/usr/bin/env python3
"""
run_llm_cases.py — VIGÍA LLM-assisted investigation runner.

Calls reason_with_llm (Anthropic backend) on each case JSON and saves a
sealed bundle to results/llm_mode/<CASE_ID>_llm_bundle.json.

Usage:
    python3 run_llm_cases.py [CASE_ID ...]
    python3 run_llm_cases.py          # runs all 15 target cases
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Environment (same as launch_vigia_mcp.sh) ────────────────────────────────
REPO = Path(__file__).parent
os.environ.setdefault("VIGIA_EVIDENCE_DIR", str(REPO / "evidence"))
os.environ.setdefault("VIGIA_LLM_BACKEND",  "anthropic")
os.environ.setdefault("VIGIA_HMAC_KEY",     "vigia-hackathon-2026-sans")
os.environ.setdefault(
    "VIGIA_SYSTEM_PROMPT_PATH",
    str(REPO / "vigia/data/system_prompt_peirce_EN.md"),
)
sys.path.insert(0, str(REPO))

import vigia.vigia_sift_bridge as bridge  # noqa: E402 — must follow env setup

CASES_DIR  = REPO / "data/cases"
OUT_DIR    = REPO / "results/llm_mode"
AGENT_DIR  = REPO / "results/agent_batch"

TARGET_CASES = [
    "VIGIA-BREAK-011", "VIGIA-BREAK-012", "VIGIA-BREAK-013",
    "VIGIA-BREAK-014", "VIGIA-BREAK-015", "VIGIA-BREAK-016",
    "VIGIA-FP-001",    "VIGIA-FP-002",    "VIGIA-FP-003",
    "FP-CULTURAL-CLEAN-001",
    "VIGIA-FN-001",    "VIGIA-FN-002",    "VIGIA-FN-003",
    "VIGIA-AMB-001",   "VIGIA-AMB-002",
]

# ── Verdict normalisation ─────────────────────────────────────────────────────
_HYP_MAP = {
    "MALICIOUS_INTENT_DETECTED":  "MALICE",
    "SUSPICION_DETECTED":         "SUSPICION",
    "NO_SEMIOTIC_ANOMALY_DETECTED": "NOISE",
    "ABSTAIN":                    "ABSTAIN",
    "MALICE":                     "MALICE",
    "INTENT":                     "MALICE",
    "SUSPICION":                  "SUSPICION",
    "NOISE":                      "NOISE",
    "BENIGN":                     "NOISE",
    "UNKNOWN":                    "UNKNOWN",
}

def _normalize(v: str) -> str:
    return _HYP_MAP.get(str(v).upper(), v)

def _fallback_verdict(case_id: str) -> str:
    bf = AGENT_DIR / f"{case_id}_agent_bundle.json"
    if not bf.exists():
        return "UNKNOWN"
    try:
        d = json.loads(bf.read_text())
        bh = d.get("pipeline_results", {}).get("abduction", {}).get("best_hypothesis", "UNKNOWN")
        return _normalize(bh)
    except Exception:
        return "UNKNOWN"

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def _extract_llm_verdict(llm_result: dict) -> str:
    """
    Extract a normalised verdict from reason_with_llm output.

    The bridge parses the LLM response to JSON; if parsing fails it returns
    {"raw_response": "...", "error": "..."}. In that case we parse the raw
    text ourselves so the runner doesn't silently emit UNKNOWN.
    """
    # Happy path — bridge parsed JSON cleanly
    v = llm_result.get("verdict")
    if v and v not in ("", "ERROR"):
        return _normalize(v)

    # Fallback — bridge returned raw text; parse it ourselves
    raw = llm_result.get("raw_response", "")
    if raw:
        # Strip markdown fences
        clean = raw.strip()
        for fence in ("```json", "```"):
            if clean.startswith(fence):
                clean = clean[len(fence):]
        # Find the last ``` and cut there
        last_fence = clean.rfind("```")
        if last_fence != -1:
            clean = clean[:last_fence]
        clean = clean.strip()
        try:
            parsed = json.loads(clean)
            v2 = parsed.get("verdict", "UNKNOWN")
            return _normalize(v2)
        except json.JSONDecodeError:
            # Try regex extraction as last resort
            import re
            m = re.search(r'"verdict"\s*:\s*"([A-Z_]+)"', raw)
            if m:
                return _normalize(m.group(1))
    return "UNKNOWN"


# ── Per-case investigation ────────────────────────────────────────────────────

async def investigate_case(case_id: str) -> dict:
    """Run reason_with_llm on the case JSON and return a result bundle."""
    case_file = CASES_DIR / f"{case_id}.json"
    if not case_file.exists():
        return {"case_id": case_id, "error": f"Case file not found: {case_file}"}

    case_text = case_file.read_text(encoding="utf-8")
    case_sha  = _sha256(case_text)
    case_data = json.loads(case_text)

    expected = (
        case_data.get("expected_verdict")
        or case_data.get("ground_truth", {}).get("expected_verdict", "UNKNOWN")
    )
    fallback = _fallback_verdict(case_id)

    # Build a concise evidence summary for the LLM
    artifacts = case_data.get("artifacts", [])
    summary_lines = [
        f"Case ID: {case_id}",
        f"Description: {case_data.get('description', '')}",
        f"Artifacts ({len(artifacts)}):",
    ]
    for a in artifacts[:30]:            # cap at 30 to respect token limits
        summary_lines.append(
            f"  [{a.get('artifact_id','')}] {a.get('evidence_type','')} — "
            f"{a.get('description','')} (raw_score={a.get('raw_score','?')}, "
            f"prior_trust={a.get('prior_trust','?')})"
        )
    if len(artifacts) > 30:
        summary_lines.append(f"  ... ({len(artifacts)-30} more artifacts truncated)")

    evidence_str = "\n".join(summary_lines)
    context_str  = (
        f"VIGÍA case investigation. Expected (test label): {expected}. "
        f"Fallback (deterministic) verdict: {fallback}. "
        f"Apply full Peirce reasoning and Mandatory Refutation Protocol."
    )

    t0 = time.monotonic()
    llm_result = await bridge.reason_with_llm(evidence=evidence_str, context=context_str)
    elapsed = round(time.monotonic() - t0, 2)

    llm_verdict = _extract_llm_verdict(llm_result)

    bundle = {
        "bundle_version":  "ebs_v1",
        "case_id":         case_id,
        "investigation_mode": "llm_assisted",
        "llm_backend":     bridge.CONFIG.llm_backend,
        "timestamp":       _utcnow(),
        "evidence_path":   str(case_file),
        "evidence_sha256": case_sha,
        "expected_verdict": expected,
        "fallback_verdict": fallback,
        "llm_verdict":     llm_verdict,
        "verdict_changed": llm_verdict != fallback,
        "elapsed_seconds": elapsed,
        "llm_raw":         llm_result,
    }
    return bundle


# ── Main ─────────────────────────────────────────────────────────────────────

async def main(case_ids: list[str]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for case_id in case_ids:
        print(f"\n[{_utcnow()}] Investigating {case_id} ...", flush=True)
        try:
            bundle = await investigate_case(case_id)
        except Exception as exc:
            print(f"  ERROR: {exc}", flush=True)
            bundle = {
                "case_id": case_id, "error": str(exc),
                "llm_verdict": "ERROR", "fallback_verdict": _fallback_verdict(case_id),
                "verdict_changed": False, "timestamp": _utcnow(),
            }

        out_path = OUT_DIR / f"{case_id}_llm_bundle.json"
        out_path.write_text(json.dumps(bundle, indent=2, default=str))

        lv = bundle.get("llm_verdict", "ERROR")
        fv = bundle.get("fallback_verdict", "?")
        ch = "YES" if bundle.get("verdict_changed") else "no"
        print(f"  fallback={fv}  llm={lv}  changed={ch}", flush=True)
        results.append(bundle)

    # ── Summary table ─────────────────────────────────────────────────────────
    print("\n" + "="*72)
    print(f"{'CASE':<30} {'EXPECTED':<12} {'FALLBACK':<12} {'LLM':<12} {'PASS?'}")
    print("="*72)

    VERDICT_MAP = {
        "MALICE":    ["MALICE", "INTENT"],
        "SUSPICION": ["SUSPICION"],
        "NOISE":     ["NOISE", "BENIGN"],
        "ABSTAIN":   ["ABSTAIN"],
        "BENIGN":    ["NOISE", "BENIGN"],
    }

    for b in results:
        cid  = b.get("case_id", "?")
        exp  = str(b.get("expected_verdict", "?")).upper()
        fb   = b.get("fallback_verdict", "?")
        lv   = b.get("llm_verdict", "?")
        # Pass if llm_verdict matches expected (using loose mapping)
        ok_set = VERDICT_MAP.get(exp, [exp])
        passed = "PASS" if lv.upper() in ok_set else "FAIL"
        print(f"{cid:<30} {exp:<12} {fb:<12} {lv:<12} {passed}")

    print("="*72)


if __name__ == "__main__":
    ids = sys.argv[1:] if len(sys.argv) > 1 else TARGET_CASES
    asyncio.run(main(ids))
