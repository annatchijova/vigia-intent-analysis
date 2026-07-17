"""
F0 (L-029 signed batch) — DARVO hardening: word-boundary matching, dead
pipeline channel retired, B-141 signal conversion fixed. Tests written RED
first against the dossier + Kimi's audit findings (docs/
PROPUESTA_L029_DARVO_20260717.md, docs/VEREDICTO_KIMI_L029_20260717.md).

Contract under test:

  A. Word-boundary keyword matching (kills the ELI false positive):
     - 'no contact' must NOT match inside "no contacts database" (the
       English plural that minted the FP);
     - 'log' must NOT match inside "logs";
     - 'server' as a standalone word still matches (documenting that ELI's
       de-annotation comes from the zero-contact side, honestly);
     - the real KIWI cases keep their exact counts and penalty;
     - the real ELI case loses pattern_present;
     - corpus census == exactly {KIWI-001, 003, 004, 005}.

  B. B-141: dict->SignalOutput conversion builds N signals from N dicts in
     BOTH deployments (pydantic in-process; dataclass via subprocess with
     pydantic masked). The old loop passed description= — a kwarg
     SignalOutput never had — so the dataclass deployment dropped EVERY
     signal via a swallowed TypeError and the pydantic deployment silently
     discarded the description.

  C. B-142: the pipeline consistency-penalty channel is retired, not
     narrowed. The penalty APIs are gone, the pipeline no longer imports
     the detector, and a schema tripwire pins that SignalOutput carries no
     description/evidence_type — if a refactor ever adds them, this test
     fails and forces re-evaluating the retired-channel decision instead
     of silently waking an uncalibrated keyword effect in the decision
     path (L-004/B-070 doctrine).
"""

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from vigia.core import darvo_detector
from vigia.core.darvo_detector import detect_darvo_pattern

REPO = Path(__file__).resolve().parent.parent


def _load_artifacts(case_file):
    return json.loads((REPO / "data" / "cases" / case_file).read_text(
        encoding="utf-8"))["artifacts"]


def _art(etype, desc):
    return {"artifact_id": "F0-A", "evidence_type": etype,
            "description": desc, "metadata": {}}


# ── A. Word-boundary matching ──────────────────────────────────────────────


class TestWordBoundaryMatching:
    def test_no_contacts_plural_does_not_match(self):
        # The exact ELI-A04 phrasing that minted the false positive.
        r = detect_darvo_pattern([_art(
            "file_metadata",
            "App content absent — no messages, no contacts database.")])
        assert r["zero_contact_count"] == 0

    def test_no_contact_as_phrase_still_matches(self):
        r = detect_darvo_pattern([_art(
            "file_metadata", "victim reports no contact since 2022")])
        assert r["zero_contact_count"] == 1

    def test_log_does_not_match_logs(self):
        # 'log' inside "logs" was the biggest generic FP source (47/201).
        r = detect_darvo_pattern([_art("log_entry", "system logs rotated daily")])
        assert r["surveillance_count"] == 0

    def test_server_standalone_word_still_matches(self):
        # Honest documentation: word boundaries do NOT kill ELI-A02's
        # 'server' ("4 S3 server list URLs" contains the standalone word).
        # ELI's de-annotation comes from the zero-contact side.
        r = detect_darvo_pattern([_art(
            "log_entry", "Psiphon proxy configured with 4 S3 server list URLs.")])
        assert r["surveillance_count"] == 1

    def test_trampolin_with_dot_boundary_matches(self):
        r = detect_darvo_pattern([_art(
            "log_entry", "PHP error logs trampolin.sg-host.com")])
        assert r["surveillance_count"] == 1


class TestRealCases:
    def test_eli_no_longer_annotated(self):
        arts = _load_artifacts("VIGIA-REAL-MAGNET-2021-IOS-ELI.json")
        r = detect_darvo_pattern(arts)
        assert r["pattern_present"] is False, (
            "ELI is a keyword-coincidence FP (dossier §1.1, Kimi §2) — the "
            "word-boundary fix must de-annotate it"
        )
        assert r["zero_contact_count"] == 0

    def test_kiwi_001_keeps_exact_annotation(self):
        r = detect_darvo_pattern(_load_artifacts("VIGIA_KIWI_001.json"))
        assert r["pattern_present"] is True
        assert r["surveillance_count"] == 2
        assert r["zero_contact_count"] >= 1
        assert r["penalty"] == Fraction(3, 5)

    def test_kiwi_003_keeps_annotation(self):
        r = detect_darvo_pattern(_load_artifacts("VIGIA_KIWI_003_AT_POV.json"))
        assert r["pattern_present"] is True
        assert r["penalty"] == Fraction(3, 5)

    def test_kiwi_002_still_blind(self):
        # The aggressor-authored bundle: no keywords, by construction.
        r = detect_darvo_pattern(
            _load_artifacts("VIGIA_KIWI_002_ZAPALLO_POV.json"))
        assert r["pattern_present"] is False
        assert r["surveillance_count"] == 0

    def test_corpus_census_exactly_four(self):
        # Permanent guard for the F0 gate: annotated set == exactly
        # {KIWI-001, 003, 004, 005}. Uses the batch runner's own corpus
        # enumeration (CASES_DIRS precedence + stem dedup).
        from run_all_agent import CASES_DIRS, find_cases
        annotated = set()
        for case_path in find_cases(CASES_DIRS):
            try:
                data = json.loads(Path(case_path).read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            arts = data.get("artifacts", [])
            if arts and detect_darvo_pattern(arts)["pattern_present"]:
                annotated.add(Path(case_path).stem)
        assert annotated == {
            "VIGIA_KIWI_001", "VIGIA_KIWI_003_AT_POV",
            "VIGIA_KIWI_004_ADV_CULPABILIDAD", "VIGIA_KIWI_005_ADV_INOCENCIA",
        }


# ── B. B-141: signal conversion in both deployments ────────────────────────


_SIGNAL_DICTS = [
    {"tool_name": "t1", "value": 1.0, "z_score": 2.0, "confidence": 0.9,
     "description": "honeypot server", "metadata": {"k": "v"}},
    {"tool_name": "t2", "value": 0.5, "z_score": 1.0, "confidence": 0.8,
     "description": "no contact", "metadata": {}},
]


class TestB141SignalConversion:
    def test_pydantic_mode_builds_all_signals(self):
        from vigia.pipeline.pipeline import _signals_from_dicts
        signals = _signals_from_dicts(list(_SIGNAL_DICTS))
        assert len(signals) == 2
        assert signals[0].tool_name == "t1"
        assert signals[1].z_score == 1.0

    def test_dataclass_mode_builds_all_signals(self):
        # Mask pydantic in a subprocess so vigia.models.ebs falls back to
        # the dataclass SignalOutput — the deployment where the old loop
        # dropped EVERY signal via swallowed TypeError.
        code = (
            "import sys; sys.modules['pydantic'] = None\n"
            "from vigia.pipeline.pipeline import _signals_from_dicts\n"
            f"sigs = _signals_from_dicts({_SIGNAL_DICTS!r})\n"
            "print(len(sigs))\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True,
            cwd=REPO, timeout=120,
        )
        assert proc.returncode == 0, proc.stderr[-2000:]
        assert proc.stdout.strip().splitlines()[-1] == "2", (
            f"stdout={proc.stdout!r} stderr={proc.stderr[-500:]!r}"
        )


# ── C. B-142: channel retired + tripwires ──────────────────────────────────


class TestB142ChannelRetired:
    def test_penalty_apis_removed(self):
        assert not hasattr(darvo_detector, "adjust_consistency_score")
        assert not hasattr(darvo_detector, "compute_darvo_penalty")

    def test_pipeline_no_longer_imports_detector(self):
        # The explanatory B-142 comment may name DARVO; what must be gone is
        # any import/call of the detector module or the retired penalty API.
        src = (REPO / "vigia" / "pipeline" / "pipeline.py").read_text(
            encoding="utf-8")
        assert "darvo_detector" not in src, (
            "the pipeline must not import the DARVO detector — the "
            "consistency-penalty channel was retired (B-142)"
        )
        assert "adjust_consistency_score" not in src

    def test_signal_output_schema_tripwire(self):
        # If SignalOutput ever grows description/evidence_type fields, the
        # retired-channel decision must be re-evaluated explicitly — a
        # refactor must not silently re-enable a description-keyword effect
        # in the decision path (L-004/B-070).
        from vigia.models.ebs import SignalOutput
        try:
            fields = set(SignalOutput.model_fields)  # pydantic v2
        except AttributeError:
            import dataclasses
            fields = {f.name for f in dataclasses.fields(SignalOutput)}
        assert "description" not in fields
        assert "evidence_type" not in fields

    def test_false_census_comment_corrected(self):
        src = (REPO / "vigia" / "core" / "darvo_detector.py").read_text(
            encoding="utf-8")
        assert "exactamente los 5" not in src, (
            "the in-code census claim was false (ELI is an FP) and must be "
            "corrected, never silently kept"
        )
