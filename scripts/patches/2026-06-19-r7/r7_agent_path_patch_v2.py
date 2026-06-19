#!/usr/bin/env python3
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

OLD = '''        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} \u2014 analysis complete.",
        )

        narrative = self._generate_narrative(results, evidence_sha256)'''

NEW = '''        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} \u2014 analysis complete.",
        )

        # R7 \u2014 deterministic devil_advocate for the agent audit-trail path.
        # sift_orchestrator.py as imported here resolves to the root-level
        # compatibility shim (confirmed by direct diff, 2026-06-19), not
        # vigia/sift/sift_orchestrator.py \u2014 CasePatternLibrary is never
        # reachable from this entry point. pattern_signal_metadata=None is
        # architecturally confirmed, not assumed. Never overwrites a
        # human-provided value because this path never had one.
        if exit_code_preview == 1 and not results.get("abduction", {}).get("devil_advocate"):
            from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
            _verdict = results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")
            results.setdefault("abduction", {})["devil_advocate"] = compose_devil_advocate_struct(
                pattern_signal_metadata=None,
                raw_verdict=_verdict,
                mapped_verdict=_verdict,
                score=results.get("pipeline_meta", {}).get("avg_score", "0"),
                confidence=results.get("abduction", {}).get("best_posterior", "0"),
                scope_note="agent audit-trail mode (vigia_agent.py \u2014 JSON-replay / autonomous path)",
            )

        narrative = self._generate_narrative(results, evidence_sha256)'''

target = Path("vigia_agent.py")
text = target.read_text(encoding="utf-8")
count = text.count(OLD)
if count != 1:
    print(f"[ABORT] anchor found {count} time(s), expected exactly 1.")
    sys.exit(1)
print("[DRY-RUN] anchor verified, exactly 1 match. OK.")
if not DRY_RUN:
    backup = target.with_suffix(target.suffix + ".bak2")
    if not backup.exists():
        backup.write_text(text, encoding="utf-8")
    target.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print(f"[OK] vigia_agent.py patched. Backup at {backup}")
