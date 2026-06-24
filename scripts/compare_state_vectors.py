import json, sys

def extract_state_vector(bundle_path):
    b = json.load(open(bundle_path))
    pr = b["pipeline_results"]
    abd = pr["abduction"]
    return {
        "verdict": abd["best_hypothesis"],
        "posterior": abd["best_posterior"],
        "confidence": abd["confidence"],
        "is_conclusive": abd["is_conclusive"],
        "artifact_count": pr["pipeline_meta"]["artifact_count"],
        "avg_score": pr["pipeline_meta"]["avg_score"],
        "signals": [
            {"artifact_id": s["artifact_id"],
             "evidence_type": s["evidence_type"],
             "z_score": s["z_score"],
             "confidence": s["confidence"]}
            for s in pr["signals"]
        ],
        "fractures": sorted(
            f.get("fracture_type", f.get("type", "unknown"))
            for f in pr.get("caie_fractures", [])
        ),
        "golden_rules": sorted(pr.get("golden_rules_triggered", [])),
        "abductive_candidates": (
            pr.get("abductive_candidates")
            or abd.get("candidates")
            or []
        ),
        "_bundle_hash_diagnostic": b.get("bundle_hash")
    }

def diff_states(a, b):
    diffs = {}
    for k in sorted(set(a) | set(b)):
        if k.startswith("_"):
            continue
        if a.get(k) != b.get(k):
            diffs[k] = {"left": a.get(k), "right": b.get(k)}
    return diffs

if __name__ == "__main__":
    paths = sys.argv[1:]
    vectors = [(p, extract_state_vector(p)) for p in paths]

    for p, sv in vectors:
        print(f"\n=== {p} ===")
        print(f"verdict: {sv['verdict']}")
        print(f"posterior: {sv['posterior']}")
        print(f"confidence: {sv['confidence']}")
        print(f"fractures: {sv['fractures']}")
        print(f"golden_rules: {sv['golden_rules']}")
        print(f"bundle_hash_diagnostic: {sv['_bundle_hash_diagnostic']}")

    baseline = vectors[0][1]
    all_identical = True
    for p, sv in vectors[1:]:
        diffs = diff_states(baseline, sv)
        if diffs:
            all_identical = False
            print(f"\nDIVERGENCE vs baseline in {p}:")
            for k, d in diffs.items():
                print(f"  {k}: {d['left']} -> {d['right']}")

    if all_identical:
        print("\nRESULT: IDENTICAL STATE VECTORS")
        print("Narrative injection did not contaminate inferential state.")
    else:
        print("\nRESULT: DIVERGENT STATE VECTORS")
        print("Narrative contamination detected.")
