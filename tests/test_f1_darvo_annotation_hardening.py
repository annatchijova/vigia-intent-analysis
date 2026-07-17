"""
F1 (L-029) — DARVO annotation hardening (tests written RED first).

The adversarial judges showed the sealed annotation carries prejudicial
force in front of a jury even with `verdict_effect: none` (dossier §5-F1,
judges FF-1/F2). Contract:

  1. The sealed `darvo_pattern` block carries a machine-readable L-004
     caveat (`trigger_class`) stating the trigger is examiner-authored
     free text with no assertion force.
  2. `devil_advocate` is MANDATORY in the block (the repo's Refutation
     Protocol applied to the only output aimed at a human role): the
     benign hypothesis is generated and sealed alongside, always.
  3. `matched_spans` gives per-keyword Daubert traceability (family,
     keyword, context window) — FIRMA decision: spans YES (transparency
     wins; the keyword list is already public in the repo).
  4. NO `attributed_actor` / nominal attribution in the sealed block
     (judge F1: an HMAC-sealed role attribution generated from free text
     is the realized defamation vector).
  5. The orchestrator narrative channel passes the new fields through.
  6. Verdict/score equality pin still holds (annotation-only).
"""

import contextlib
import io
import json
from pathlib import Path

from vigia.core.darvo_detector import detect_darvo_pattern
from vigia_scorer import _vigia_score

REPO = Path(__file__).resolve().parent.parent


def _kiwi001_artifacts():
    return json.loads(
        (REPO / "data" / "cases" / "VIGIA_KIWI_001.json").read_text(
            encoding="utf-8")
    )["artifacts"]


def _score(case):
    with contextlib.redirect_stdout(io.StringIO()), \
         contextlib.redirect_stderr(io.StringIO()):
        return _vigia_score(case)


class TestDetectorMatchedSpans:
    def test_spans_present_with_family_keyword_context(self):
        r = detect_darvo_pattern(_kiwi001_artifacts())
        spans = r["matched_spans"]
        assert spans, "matched_spans must accompany every detection"
        families = {s["family"] for s in spans}
        assert families == {"surveillance", "zero_contact"}
        keywords = {s["keyword"] for s in spans}
        # KIWI-001-A02: 'php error' + 'trampolin'; A04: 'honeypot' +
        # 'accesos' (surveillance) and 'bloqueado' (zero-contact).
        assert {"php error", "trampolin", "honeypot", "accesos",
                "bloqueado"} <= keywords
        for s in spans:
            assert s["artifact_id"]
            assert s["keyword"] in s["context"]

    def test_no_spans_when_no_matches(self):
        r = detect_darvo_pattern([{
            "artifact_id": "X", "evidence_type": "log_entry",
            "description": "registro de eventos del sistema", "metadata": {},
        }])
        assert r["matched_spans"] == []


class TestSealedBlockHardening:
    def _block(self):
        case = {"case_id": "F1-CASE", "artifacts": _kiwi001_artifacts()}
        return _score(case)["darvo_pattern"]

    def test_trigger_class_caveat_sealed(self):
        block = self._block()
        assert "L-004" in block["trigger_class"]
        assert "no assertion force" in block["trigger_class"]

    def test_devil_advocate_mandatory_and_benign(self):
        block = self._block()
        da = block["devil_advocate"]
        assert da and len(da) > 80, "devil_advocate must be substantive"
        assert "benign" in da.lower() or "benigna" in da.lower()
        # It must name the core epistemic limit of the trigger.
        assert "narration" in da.lower() or "narración" in da.lower()

    def test_matched_spans_sealed(self):
        block = self._block()
        assert block["matched_spans"]
        assert all("keyword" in s and "family" in s
                   for s in block["matched_spans"])

    def test_no_nominal_attribution(self):
        block = self._block()
        assert "attributed_actor" not in block
        assert "role_attribution" not in block


class TestNarrativeChannelPassthrough:
    def test_orchestrator_summary_carries_new_fields(self):
        from sift_orchestrator import _motor_darvo_summary
        motor = {"darvo_pattern": {
            "penalty": "3/5", "surveillance_count": 2, "zero_contact_count": 1,
            "matched_artifacts": ["A02", "A04"],
            "matched_spans": [{"artifact_id": "A02", "family": "surveillance",
                               "keyword": "honeypot", "context": "blog honeypot x"}],
            "trigger_class": "examiner-authored free text (L-004 applies); no assertion force",
            "devil_advocate": "Benign hypothesis: ...",
            "verdict_effect": "none (FW-009 Fase 1 — annotation only)",
        }}
        s = _motor_darvo_summary(motor)
        assert s["trigger_class"].startswith("examiner-authored")
        assert s["devil_advocate"].startswith("Benign")
        assert s["matched_spans"]
