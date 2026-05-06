#!/usr/bin/env python3
"""
scripts/generate_report.py
===========================
VIGÍA — Genera el reporte Amicus Curiae desde los resultados de los casos.

Uso:
    python generate_report.py                      # todos los casos
    python generate_report.py --output report.json # guardar JSON

El reporte incluye:
  - Veredicto por caso con Peirce chain
  - Comparación VIGÍA vs naive baseline
  - MITRE ATT&CK TTPs detectadas
  - Narrativa Amicus Curiae en texto

SANS FIND EVIL Hackathon 2026
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from run_vigia_case import _vigia_score, _naive_score

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def generate_amicus_narrative(case: dict, result: dict) -> str:
    """Genera narrativa Amicus Curiae para un caso forense."""
    pc = case.get("peirce_chain", {})
    verdict = result["verdict"]
    score = result["score"]
    conf = result["confidence"]
    violations = case.get("temporal_violations", [])
    fractures = case.get("caie_fractures", [])

    lines = [
        f"AMICUS CURIAE — {case.get('name', case.get('case_id', 'Unknown'))}",
        "=" * 60,
        "",
        "FORENSIC OPINION",
        "-" * 40,
    ]

    # Verdict block
    lines.append(f"This system concludes with {conf:.0%} confidence: {verdict}")
    lines.append(f"Composite Intent Score: {score:.4f}")
    lines.append("")

    # Peirce reasoning
    if pc:
        lines.append("ABDUCTIVE REASONING (Peirce Framework):")
        if pc.get("firstness"):
            lines.append(f"  Firstness  (phenomenon) : {pc['firstness']}")
        if pc.get("secondness"):
            lines.append(f"  Secondness (context)    : {pc['secondness']}")
        if pc.get("thirdness"):
            lines.append(f"  Thirdness  (inference)  : {pc['thirdness']}")
        lines.append("")

    # Temporal violations
    if violations:
        lines.append("TEMPORAL INTEGRITY ANALYSIS:")
        for v in violations:
            severity_desc = "CRITICAL" if v.get("severity", 0) >= 0.9 else "SIGNIFICANT"
            lines.append(f"  [{severity_desc}] {v.get('type', '?')} (severity={v.get('severity', 0):.2f})")
            interp = v.get("interpretation", "")
            if interp:
                lines.append(f"    → {interp[:120]}")
        lines.append("")

    # CAIE fractures
    if fractures:
        lines.append("CROSS-ARTIFACT INCONGRUENCE:")
        for f in fractures:
            lines.append(f"  [{f.get('fracture_type', '?')}] severity={f.get('severity', 0):.2f}")
            interp = f.get("interpretation", "")
            if interp:
                lines.append(f"    → {interp[:120]}")
        lines.append("")

    # MITRE TTPs
    ttps = case.get("expected_mitre_ttps", [])
    if ttps:
        lines.append(f"MITRE ATT&CK TTPs DETECTED: {', '.join(ttps)}")
        lines.append("")

    # Hard gate
    if result.get("hard_temporal_gate"):
        lines.append("HARD GATE TRIGGERED: EFFECT_BEFORE_CAUSE")
        lines.append("Physical law violation detected. Evidence timeline is impossible.")
        lines.append("This finding alone is sufficient to flag the evidence as manipulated.")
        lines.append("")

    # Provenance
    prov = case.get("provenance_analysis", {})
    if prov:
        lines.append(f"CHAIN OF CUSTODY: {prov.get('chain_status', 'UNKNOWN')}")
        if prov.get("effective_trust") is not None:
            lines.append(f"  Effective Trust: {prov['effective_trust']:.2f}")
        if prov.get("reason"):
            lines.append(f"  Reason: {prov['reason'][:100]}")
        lines.append("")

    lines.append(f"Generated: {_utcnow()}")
    lines.append("System: VIGÍA v2.0 — SANS FIND EVIL Hackathon 2026")
    return "\n".join(lines)


def generate_report(cases_dir: str, output_path: str | None = None) -> dict:
    cases_path = Path(cases_dir)
    case_files = sorted(cases_path.glob("*.json"))

    if not case_files:
        print(f"No case files in {cases_dir}")
        return {}

    report = {
        "title": "VIGÍA Forensic Investigation Report",
        "subtitle": "SANS FIND EVIL Hackathon 2026",
        "generated_at": _utcnow(),
        "system_version": "2.0.0",
        "methodology": "Adversarial Forensic Epistemology (Peirce + Bayesian Trust Fusion + CAIE)",
        "cases": [],
        "summary": {},
    }

    total = 0
    correct = 0
    verdict_changes = 0
    mean_delta = 0.0

    for cf in case_files:
        with open(cf, encoding="utf-8") as f:
            case = json.load(f)

        result = _vigia_score(case)
        naive = _naive_score(case.get("artifacts", []))
        expected = case.get("expected_verdict", "?")
        is_correct = result["verdict"] == expected
        delta = result["score"] - naive

        naive_verdict = (
            "MALICE" if naive > 0.65 else
            "SUSPICION" if naive > 0.35 else
            "NOISE"
        )
        changed = naive_verdict != result["verdict"]

        case_report = {
            "case_id": case.get("case_id"),
            "name": case.get("name"),
            "description": case.get("description", ""),
            "verdict": result["verdict"],
            "score": result["score"],
            "confidence": result["confidence"],
            "reason": result["reason"],
            "expected_verdict": expected,
            "correct": is_correct,
            "naive_score": naive,
            "naive_verdict": naive_verdict,
            "verdict_changed_from_naive": changed,
            "delta_from_naive": round(delta, 4),
            "hard_temporal_gate": result.get("hard_temporal_gate", False),
            "mean_effective_trust": result.get("mean_effective_trust", 0),
            "fracture_malice_boost": result.get("fracture_malice_boost", 0),
            "temporal_violations_count": result.get("temporal_violations", 0),
            "caie_fractures_count": result.get("caie_fractures", 0),
            "peirce_chain": case.get("peirce_chain", {}),
            "expected_mitre_ttps": case.get("expected_mitre_ttps", []),
            "amicus_curiae_narrative": generate_amicus_narrative(case, result),
        }

        report["cases"].append(case_report)

        total += 1
        if is_correct:
            correct += 1
        if changed:
            verdict_changes += 1
        mean_delta += delta

    mean_delta = round(mean_delta / total, 4) if total else 0.0

    report["summary"] = {
        "total_cases": total,
        "correct_verdicts": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "verdict_changes_from_naive": verdict_changes,
        "mean_delta_from_naive": mean_delta,
        "hard_temporal_gates_triggered": sum(
            1 for c in report["cases"] if c["hard_temporal_gate"]
        ),
        "mean_effective_trust": round(
            sum(c["mean_effective_trust"] for c in report["cases"]) / total, 4
        ) if total else 0.0,
        "key_insight": (
            "VIGÍA separates forensic evaluation into four dimensions: "
            "temporal causality, provenance integrity, correlation independence, and trust fusion. "
            f"Accuracy: {correct}/{total}. "
            f"Verdict changes from naive: {verdict_changes}/{total}. "
            "This is not detection. This is adversarial forensic reasoning."
        ),
    }

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to: {output_path}")
    else:
        # Print human-readable summary
        print("\n" + "=" * 72)
        print("  VIGÍA FORENSIC INVESTIGATION REPORT")
        print("  SANS FIND EVIL Hackathon 2026")
        print("=" * 72)
        for case in report["cases"]:
            print(f"\n{'─' * 60}")
            print(case["amicus_curiae_narrative"])

        s = report["summary"]
        print("\n" + "=" * 72)
        print(f"  SUMMARY: {s['correct_verdicts']}/{s['total_cases']} correct "
              f"| {s['verdict_changes_from_naive']} verdict changes from naive "
              f"| accuracy={s['accuracy']:.0%}")
        print(f"\n  {s['key_insight']}")
        print("=" * 72 + "\n")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera reporte Amicus Curiae VIGÍA")
    parser.add_argument("--cases-dir", default="cases")
    parser.add_argument("--output", help="Guardar JSON en este path")
    args = parser.parse_args()
    generate_report(args.cases_dir, args.output)


if __name__ == "__main__":
    main()
