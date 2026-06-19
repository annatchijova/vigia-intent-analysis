#!/usr/bin/env python3
"""
r7_pipeline_patch.py — R7 patch, pipeline.py injection (follow-up to
r7_devil_advocate_patch.py, which already ran successfully on the other
4 files).

Confirmed by direct audit, 2026-06-19: pipeline.py has zero references to
CasePatternLibrary, case_pattern_library, or sift_orchestrator. Pattern
data is therefore structurally unavailable on this path too — same finding
as vigia_scorer.py / build_bundle(). pattern_signal_metadata is passed as
None; the composer falls back to the explicit scope-limitation narrative.

NOTE — one assumption not independently confirmed for this specific file:
decision_trace.decision and decision_trace.posterior are assumed to exist
on this DecisionTrace instance, by analogy with build_bundle.py's usage.
There are 4 distinct DecisionTrace class definitions in this repo (separate
P0 cleanup item) and this file's instance was not read field-by-field this
session. The dry-run below only verifies the text anchor exists once — it
cannot catch an AttributeError at runtime. Run a real MALICE-verdict case
through the full pipeline after applying, before trusting this in
production.

Usage:
    cd ~/vigia-repo
    python3 r7_pipeline_patch.py --dry-run
    python3 r7_pipeline_patch.py
"""
import sys
import shutil
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
REPO = Path(__file__).resolve().parent


def patch_file(path: str, replacements: list[tuple[str, str]]) -> None:
    fpath = REPO / path
    if not fpath.exists():
        raise SystemExit(f"ABORT: {fpath} does not exist")
    original = fpath.read_text(encoding="utf-8")
    text = original
    for old, new in replacements:
        count = text.count(old)
        if count == 0:
            raise SystemExit(f"ABORT: anchor not found in {path}:\n{old[:200]}")
        if count > 1:
            raise SystemExit(f"ABORT: ambiguous anchor ({count} matches) in {path}:\n{old[:200]}")
        text = text.replace(old, new)
    if DRY_RUN:
        print(f"[DRY-RUN] {path} — {len(replacements)} replacement(s) verified, anchor(s) unique. OK.")
        return
    backup = fpath.with_suffix(fpath.suffix + ".bak")
    shutil.copy2(fpath, backup)
    fpath.write_text(text, encoding="utf-8")
    print(f"[OK] {path} patched. Backup at {backup}")


patch_file(
    "vigia/pipeline/pipeline.py",
    [(
        '''        # Preparar CAIE analysis si está disponible
        caie_analysis = None
        if hasattr(self, '_last_caie_result') and self._last_caie_result:
            caie_analysis = {
                "verdict": self._last_caie_result.get("verdict"),
                "structural_verdict": self._last_caie_result.get("structural_verdict"),
                "composite_score": self._last_caie_result.get("composite_score"),
                "fractures_detected": self._last_caie_result.get("fractures_detected", 0),
                "golden_rules_triggered": self._last_caie_result.get("golden_rules_triggered", 0),
                "fractures": self._last_caie_result.get("fractures", []),
                "key_fractures": [
                    {
                        "type": f.get("type"),
                        "severity": f.get("severity"),
                        "artifact_a": f.get("artifact_a", "")[:100],
                        "artifact_b": f.get("artifact_b", "")[:100],
                    }
                    for f in self._last_caie_result.get("fractures", [])[:5]
                ],
            }''',
        '''        # Preparar CAIE analysis si está disponible
        caie_analysis = None
        if hasattr(self, '_last_caie_result') and self._last_caie_result:
            caie_analysis = {
                "verdict": self._last_caie_result.get("verdict"),
                "structural_verdict": self._last_caie_result.get("structural_verdict"),
                "composite_score": self._last_caie_result.get("composite_score"),
                "fractures_detected": self._last_caie_result.get("fractures_detected", 0),
                "golden_rules_triggered": self._last_caie_result.get("golden_rules_triggered", 0),
                "fractures": self._last_caie_result.get("fractures", []),
                "key_fractures": [
                    {
                        "type": f.get("type"),
                        "severity": f.get("severity"),
                        "artifact_a": f.get("artifact_a", "")[:100],
                        "artifact_b": f.get("artifact_b", "")[:100],
                    }
                    for f in self._last_caie_result.get("fractures", [])[:5]
                ],
            }

            # R7 — deterministic devil_advocate. pattern_signal_metadata is
            # always None here: CasePatternLibrary never runs inside
            # pipeline.py (confirmed by direct audit, 2026-06-19 — no
            # reference to CasePatternLibrary/case_pattern_library/
            # sift_orchestrator anywhere in this file). It only runs inside
            # sift_orchestrator.py, a separate, currently unconnected path.
            # See KNOWN_LIMITATIONS.md. The composer falls back to an
            # explicit scope-limitation narrative instead of a generic
            # template.
            if caie_analysis.get("verdict") in ("MALICE", "INTENT"):
                from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
                caie_analysis["devil_advocate"] = compose_devil_advocate_struct(
                    pattern_signal_metadata=None,
                    raw_verdict=caie_analysis.get("verdict", "UNKNOWN"),
                    mapped_verdict=decision_trace.decision,
                    score=caie_analysis.get("composite_score", 0.0),
                    confidence=decision_trace.posterior,
                )''',
    )],
)

print("\nDone." if not DRY_RUN else "\nDry-run OK — anchor exists exactly once.")
print("REMINDER: decision_trace.decision / .posterior attribute existence on this")
print("specific instance was not independently confirmed this session. Test with a")
print("real MALICE-verdict case before relying on this in production.")
