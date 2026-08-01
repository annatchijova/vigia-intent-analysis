"""B-127 dry-run: score all 199 cases with Grice injection, compare against baseline."""
import json, sys, asyncio, os, logging, io

os.environ.setdefault("VIGIA_EVIDENCE_DIR", "/tmp/vigia_dry")
os.makedirs("/tmp/vigia_dry", exist_ok=True)

# Suppress noisy logging during mass scoring
logging.disable(logging.WARNING)
_real_stderr = sys.stderr

sys.stderr = io.StringIO()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vigia.vigia_sift_bridge import audit_grice_maxims
from vigia_scorer import _vigia_score, _normalize_case
sys.stderr = _real_stderr
logging.disable(logging.NOTSET)

_TT = {"cultural_marker", "log_entry", "document_geometry", "testimony"}


def _cmp(expected: str, got: str) -> bool:
    e, g = expected.upper(), got.upper()
    if e == g:
        return True
    if e == "UNKNOWN":
        return True
    if e == "INTENT" and g == "MALICE":
        return True
    if e == "BENIGN" and g == "NOISE":
        return True
    return False


def main():
    with open("results/agent_batch/_batch_summary.json") as f:
        summary = json.load(f)

    changed = []
    passed_new = 0
    total = 0
    grice_injected = 0

    for r in summary["results"]:
        cid = r["case_id"]
        total += 1

        case = None
        for cp in [f"data/cases/converted/{cid}.json", f"data/cases/{cid}.json"]:
            try:
                with open(cp) as f:
                    case = json.load(f)
                break
            except FileNotFoundError:
                continue

        if case is None:
            if r.get("pass", False):
                passed_new += 1
            continue

        # Some files contain a list of cases — find the matching one
        if isinstance(case, list):
            match = [c for c in case if isinstance(c, dict) and c.get("case_id") == cid]
            if match:
                case = match[0]
            else:
                if r.get("pass", False):
                    passed_new += 1
                continue

        expected = str(case.get("expected_verdict", r.get("expected", "?"))).upper()

        try:
            sys.stderr = io.StringIO()
            case_norm = _normalize_case(case)
            sys.stderr = _real_stderr
        except Exception:
            sys.stderr = _real_stderr
            case_norm = dict(case)

        blind = {k: v for k, v in case_norm.items() if k != "expected_verdict"}
        arts = blind.get("artifacts", [])

        # B-127: inject Grice for testimony-only, non-exculpatory cases
        if (
            isinstance(arts, list)
            and arts
            and all(
                isinstance(a, dict) and str(a.get("evidence_type", "")).lower() in _TT
                for a in arts
            )
            and not any(
                isinstance(a, dict) and str(a.get("semantic_role", "")).lower() == "exculpatory"
                for a in arts
            )
        ):
            msgs = [
                a.get("description", "")
                for a in arts
                if isinstance(a, dict) and a.get("description")
            ]
            if msgs:
                try:
                    gr = asyncio.run(audit_grice_maxims(msgs))
                    blind["grice_verdict"] = gr.get("verdict", "")
                    blind["grice_deception_probability"] = gr.get("probability_deception", 0)
                    # B-225 / L-070: este script SÍ corre el auditor en vivo
                    # (audit_grice_maxims arriba), así que marca la
                    # procedencia. Sin el marcador el scorer trataría el
                    # resultado como una declaración no verificada y abstendría.
                    blind["grice_source"] = "live_grice"
                    grice_injected += 1
                except Exception:
                    pass

        try:
            sys.stderr = io.StringIO()
            result = _vigia_score(blind)
            sys.stderr = _real_stderr
            new_verdict = result.get("verdict", "?")
        except Exception:
            sys.stderr = _real_stderr
            if r.get("pass", False):
                passed_new += 1
            continue

        old_verdict = r.get("got", "?")
        new_pass = _cmp(expected, new_verdict)
        if new_pass:
            passed_new += 1

        if old_verdict != new_verdict:
            old_pass = r.get("pass", False)
            if new_pass and not old_pass:
                d = "FIX"
            elif old_pass and not new_pass:
                d = "REGRESSION"
            else:
                d = "NEUTRAL"
            changed.append(
                {
                    "case_id": cid,
                    "expected": expected,
                    "old": old_verdict,
                    "new": new_verdict,
                    "direction": d,
                }
            )

    print(f"Total: {total}, Passed: {passed_new} (was 185)")
    print(f"Grice injected: {grice_injected} cases")
    print(f"Changed verdicts: {len(changed)}")
    for c in changed:
        print(
            f'  {c["case_id"]:55s} {c["expected"]:10s} '
            f'{c["old"]:10s} -> {c["new"]:10s} {c["direction"]}'
        )
    regressions = [c for c in changed if c["direction"] == "REGRESSION"]
    if regressions:
        print(f"\n*** REGRESSIONS: {len(regressions)} ***")
        for c in regressions:
            print(f'  {c["case_id"]}')
        sys.exit(1)
    else:
        print("\nNo regressions.")


if __name__ == "__main__":
    main()
