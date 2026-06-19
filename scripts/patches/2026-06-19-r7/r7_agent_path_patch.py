#!/usr/bin/env python3
"""
r7_agent_path_patch.py — Surgical patch, 4 files, fail-fast anchors.
"""
import sys
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv

PATCHES = [
    (
        "vigia/core/devil_advocate_gen.py",
        '''    score: float,
    confidence: float,
    k: int = K_DEFAULT,
) -> Dict[str, Any]:''',
        '''    score: float,
    confidence: float,
    k: int = K_DEFAULT,
    scope_note: str = "standalone scorer mode",
) -> Dict[str, Any]:''',
        "add scope_note param to function signature",
    ),
    (
        "vigia/core/devil_advocate_gen.py",
        '''    elif pattern_signal_metadata is None:
        narrative = (
            f"Eco's Razor (Abductive Falsification) applied to verdict {mapped_verdict}. "
            "Pattern-matching data was not available on this code path — "
            "CasePatternLibrary is not invoked here by design (standalone scorer mode; "
            "see KNOWN_LIMITATIONS.md). No structured counter-hypothesis could be "
            "derived deterministically. This is a documented scope limitation of the "
            "current code path, not an absence of falsification attempt."
        )''',
        '''    elif pattern_signal_metadata is None:
        narrative = (
            f"Eco's Razor (Abductive Falsification) applied to verdict {mapped_verdict}. "
            "Pattern-matching data was not available on this code path — "
            f"CasePatternLibrary is not invoked here by design ({scope_note}; "
            "see KNOWN_LIMITATIONS.md). No structured counter-hypothesis could be "
            "derived deterministically. This is a documented scope limitation of the "
            "current code path, not an absence of falsification attempt."
        )''',
        "use scope_note in narrative instead of hardcoded text",
    ),
    (
        "vigia/pipeline/pipeline.py",
        '''                caie_analysis["devil_advocate"] = compose_devil_advocate_struct(
                    pattern_signal_metadata=None,
                    raw_verdict=caie_analysis.get("verdict", "UNKNOWN"),
                    mapped_verdict=decision_trace.decision,
                    score=caie_analysis.get("composite_score", 0.0),
                    confidence=decision_trace.posterior,
                )''',
        '''                caie_analysis["devil_advocate"] = compose_devil_advocate_struct(
                    pattern_signal_metadata=None,
                    raw_verdict=caie_analysis.get("verdict", "UNKNOWN"),
                    mapped_verdict=decision_trace.decision,
                    score=caie_analysis.get("composite_score", 0.0),
                    confidence=decision_trace.posterior,
                    scope_note="standalone scorer mode (vigia/pipeline/pipeline.py)",
                )''',
        "explicit scope_note in pipeline.py call site",
    ),
    (
        "vigia/core/bundle_builder.py",
        '''        caie_payload["devil_advocate"] = compose_devil_advocate_struct(
            pattern_signal_metadata=None,
            raw_verdict=raw_verdict,
            mapped_verdict=decision_verdict,
            score=score,
            confidence=confidence,
        )''',
        '''        caie_payload["devil_advocate"] = compose_devil_advocate_struct(
            pattern_signal_metadata=None,
            raw_verdict=raw_verdict,
            mapped_verdict=decision_verdict,
            score=score,
            confidence=confidence,
            scope_note="standalone scorer mode (vigia/core/bundle_builder.py build_bundle())",
        )''',
        "explicit scope_note in bundle_builder.py call site",
    ),
    (
        "vigia_agent.py",
        '''        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} — analysis complete.",
        )
        narrative = self._generate_narrative(results, evidence_sha256)''',
        '''        self.audit.log(
            action="AGENT_EXIT",
            tool="vigia_agent",
            inputs={"verdict": results.get("abduction", {}).get("best_hypothesis", "UNKNOWN")},
            outputs={"exit_code": exit_code_preview},
            iteration=self.iteration,
            note=f"Exit code {exit_code_preview} — analysis complete.",
        )
        # R7 — deterministic devil_advocate for the agent audit-trail path.
        # sift_orchestrator.py as imported here resolves to the root-level
        # compatibility shim (confirmed by direct diff, 2026-06-19), not
        # vigia/sift/sift_orchestrator.py — CasePatternLibrary is never
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
                scope_note="agent audit-trail mode (vigia_agent.py — JSON-replay / autonomous path)",
            )
        narrative = self._generate_narrative(results, evidence_sha256)''',
        "new call site: devil_advocate for the agent audit-trail path",
    ),
]


def main():
    repo_root = Path.cwd()
    for rel_path, old_str, new_str, description in PATCHES:
        target = repo_root / rel_path
        if not target.exists():
            print(f"[ABORT] {rel_path} does not exist at {target}")
            sys.exit(1)
        text = target.read_text(encoding="utf-8")
        count = text.count(old_str)
        if count != 1:
            print(f"[ABORT] {rel_path} — anchor for '{description}' found {count} time(s), expected exactly 1.")
            sys.exit(1)
        print(f"[DRY-RUN] {rel_path} — 1 replacement verified ({description}). OK.")
        if not DRY_RUN:
            backup = target.with_suffix(target.suffix + ".bak")
            if not backup.exists():
                backup.write_text(text, encoding="utf-8")
            new_text = text.replace(old_str, new_str, 1)
            target.write_text(new_text, encoding="utf-8")
            print(f"[OK] {rel_path} patched. Backup at {backup}")
    print("Dry-run OK — all anchors exist exactly once." if DRY_RUN else "Done.")


if __name__ == "__main__":
    main()
