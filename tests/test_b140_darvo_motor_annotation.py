"""
B-140 (L-029 / FW-009 Fase 1) — DARVO visible in the Mode 1 motor path
(tests written RED first).

Firstness: `darvo_detector.compute_darvo_penalty` reads artifact fields
with getattr() only. The Mode 1 (EBS JSON) path passes artifacts as plain
dicts, so the detector was structurally blind there: KIWI-001-A02
("PHP error ... trampolin", log_entry) and KIWI-001-A04
("Blog honeypot ... accesos ... bloqueado", file_metadata) carry the exact
keywords the detector looks for, and none of them ever fired outside the
pipeline path.

Contract under test (Fase 1 — ANNOTATION ONLY, no verdict effect; the
verdict effect and the false_flag relational verdict remain doctrine
decisions per KNOWN_LIMITATIONS L-029):

  1. `detect_darvo_pattern()` reads dicts AND objects; the object
     (pipeline) behavior is pinned unchanged — same penalties as the
     pre-B-140 implementation.
  2. `_vigia_score` adds a `darvo_pattern` block when the asymmetry is
     present, and the block changes NEITHER verdict NOR score
     (equality pin against a keyword-scrubbed twin case).
  3. The orchestrator summary helper translates the scorer block to the
     narrative channel (same B-094 shape), returning None when absent.
  4. Real case: scripts/VIGIA_KIWI_001.json produces the annotation with
     the L-029 numbers (2 surveillance artifacts, zero-contact present,
     penalty 3/5).
"""

import contextlib
import io
import json
from fractions import Fraction
from pathlib import Path

from vigia.core.darvo_detector import detect_darvo_pattern
from vigia_scorer import _vigia_score

REPO = Path(__file__).resolve().parent.parent


# ── Artifact builders ───────────────────────────────────────────────────────


def _dict_art(i, etype, desc, raw="0.3"):
    return {
        "artifact_id": f"B140-A{i:02d}", "evidence_type": etype,
        "raw_score": raw, "prior_trust": "0.8",
        "source_tool": "manual_forensic_review", "description": desc,
        "timestamp": f"2026-01-0{(i % 8) + 1}T00:00:00Z",
        "provenance_chain": ["acq"], "metadata": {},
    }


class _ObjArt:
    """Legacy pipeline shape: attribute access only (SignalOutput-like)."""

    def __init__(self, etype, desc):
        self.evidence_type = etype
        self.description = desc
        self.metadata = {}


def _score(case):
    with contextlib.redirect_stdout(io.StringIO()), \
         contextlib.redirect_stderr(io.StringIO()):
        return _vigia_score(case)


# ── 1. Detector: dict support + pinned object behavior ─────────────────────


class TestDetectorDictSupport:
    def test_dict_surveillance_fires(self):
        arts = [_dict_art(1, "log_entry", "PHP error logs con usuario trampolin")]
        r = detect_darvo_pattern(arts)
        assert r["surveillance_count"] == 1
        assert r["penalty"] == Fraction(1, 10)
        # Surveillance keywords ALONE are not the DARVO asymmetry: 47/201
        # corpus cases (incl. benign) match generic keywords like 'log'.
        # pattern_present demands BOTH sides (measured census 2026-07-17).
        assert r["pattern_present"] is False

    def test_pattern_present_requires_full_asymmetry(self):
        arts = [
            _dict_art(1, "log_entry", "server log de stalkeo"),
            _dict_art(2, "file_metadata", "honeypot accesos, actor bloqueado"),
        ]
        assert detect_darvo_pattern(arts)["pattern_present"] is True

    def test_dict_zero_contact_multiplier(self):
        arts = [
            _dict_art(1, "log_entry", "server log de stalkeo"),
            _dict_art(2, "file_metadata", "honeypot con 60 accesos, actor bloqueado"),
        ]
        r = detect_darvo_pattern(arts)
        assert r["surveillance_count"] == 2
        assert r["zero_contact_count"] == 1
        assert r["penalty"] == Fraction(6, 10)

    def test_penalty_capped_at_8_10(self):
        arts = [
            _dict_art(i, "log_entry", "honeypot server log, usuario bloqueado")
            for i in range(1, 4)
        ]
        r = detect_darvo_pattern(arts)
        assert r["surveillance_count"] == 3
        assert r["penalty"] == Fraction(8, 10)

    def test_zero_contact_alone_is_no_pattern(self):
        arts = [_dict_art(1, "cultural_marker", "cero contacto desde 2022")]
        r = detect_darvo_pattern(arts)
        assert r["surveillance_count"] == 0
        assert r["penalty"] == Fraction(0)
        assert r["pattern_present"] is False

    def test_surveillance_needs_matching_evidence_type(self):
        # Keywords present but evidence_type outside file_metadata/log_entry.
        arts = [_dict_art(1, "cultural_marker", "honeypot server accesos")]
        assert detect_darvo_pattern(arts)["surveillance_count"] == 0

    def test_matched_artifacts_traceability(self):
        arts = [
            _dict_art(1, "log_entry", "php error trampolin"),
            _dict_art(2, "document_visual", "foto del parque"),
        ]
        assert detect_darvo_pattern(arts)["matched_artifacts"] == ["B140-A01"]

    def test_malformed_fields_do_not_crash(self):
        weird = [
            {"artifact_id": "W1", "evidence_type": "log_entry",
             "description": None, "metadata": "not-a-dict"},
            {"description": 42, "metadata": None},
            {},
        ]
        r = detect_darvo_pattern(weird)
        assert r["penalty"] == Fraction(0)

    def test_object_path_still_detected(self):
        # F0 note: the pipeline penalty APIs (compute_darvo_penalty,
        # adjust_consistency_score) were RETIRED in the F0 signed batch
        # (B-142 — the channel was dead at runtime). Object-shaped
        # artifacts must still be readable by the annotation detector.
        one = [_ObjArt("log_entry", "server log de stalkeo")]
        assert detect_darvo_pattern(one)["penalty"] == Fraction(1, 10)
        both = one + [_ObjArt("file_metadata", "honeypot accesos, bloqueado")]
        r = detect_darvo_pattern(both)
        assert r["penalty"] == Fraction(6, 10)
        assert r["pattern_present"] is True

    def test_metadata_evidence_type_fallback(self):
        art = {"artifact_id": "M1", "description": "honeypot accesos",
               "metadata": {"evidence_type": "log_entry"}}
        assert detect_darvo_pattern([art])["surveillance_count"] == 1


# ── 2. Scorer annotation: present, faithful, and verdict-neutral ───────────


def _darvo_case():
    return {
        "case_id": "B140-CASE",
        "artifacts": [
            _dict_art(1, "log_entry", "PHP error logs trampolin server", "0.7"),
            _dict_art(2, "file_metadata",
                      "Blog honeypot: 60 accesos diarios desde actor bloqueado",
                      "0.6"),
            _dict_art(3, "cultural_marker", "imagen con texto legal", "0.3"),
        ],
    }


def _scrubbed_twin():
    case = _darvo_case()
    neutral = ["registro de eventos del sistema web",
               "actividad diaria registrada en el sitio",
               "imagen con texto legal"]
    for art, desc in zip(case["artifacts"], neutral):
        art["description"] = desc
    return case


class TestScorerAnnotation:
    def test_annotation_present_with_pattern(self):
        result = _score(_darvo_case())
        block = result.get("darvo_pattern")
        assert block is not None
        assert block["surveillance_count"] == 2
        assert block["zero_contact_count"] == 1
        assert block["penalty"] == "3/5"
        assert "B140-A01" in block["matched_artifacts"]

    def test_annotation_absent_without_pattern(self):
        assert "darvo_pattern" not in _score(_scrubbed_twin())

    def test_annotation_absent_for_surveillance_only(self):
        # Generic surveillance keywords without a zero-contact claim must
        # NOT be annotated as DARVO (47 corpus cases incl. benign match
        # them — a misleading narrative block would be worse than none).
        case = _darvo_case()
        case["artifacts"][1]["description"] = "registro estable del servidor"
        result = _score(case)
        assert "darvo_pattern" not in result

    def test_annotation_only_verdict_and_score_identical(self):
        with_pattern = _score(_darvo_case())
        without = _score(_scrubbed_twin())
        assert with_pattern["verdict"] == without["verdict"]
        assert with_pattern["score"] == without["score"]
        assert with_pattern["confidence"] == without["confidence"]


# ── 3. Orchestrator summary helper (narrative channel, B-094 shape) ────────


class TestOrchestratorSummary:
    def test_none_when_absent(self):
        from sift_orchestrator import _motor_darvo_summary
        assert _motor_darvo_summary({}) is None
        assert _motor_darvo_summary({"verdict": "NOISE"}) is None
        assert _motor_darvo_summary(None) is None

    def test_summary_shape(self):
        from sift_orchestrator import _motor_darvo_summary
        motor = {"darvo_pattern": {
            "penalty": "3/5", "surveillance_count": 2,
            "zero_contact_count": 1, "matched_artifacts": ["A02", "A04"],
            "verdict_effect": "none (FW-009 Fase 1 — annotation only)",
        }}
        s = _motor_darvo_summary(motor)
        assert s["status"] == "OK"
        assert s["source"] == "motor_darvo_annotation"
        assert s["penalty"] == "3/5"
        assert "daubert_note" in s and "NOT modified" in s["daubert_note"]


# ── 4. Real case: KIWI-001 (the L-029 discovery case) ──────────────────────


class TestKiwi001RealCase:
    def test_kiwi001_annotation_matches_l029(self):
        case = json.loads(
            (REPO / "scripts" / "VIGIA_KIWI_001.json").read_text(encoding="utf-8")
        )
        result = _score(case)
        block = result.get("darvo_pattern")
        assert block is not None, (
            "KIWI-001 carries the canonical DARVO asymmetry (L-029) — the "
            "motor path must annotate it"
        )
        # A02 (log_entry: 'PHP error ... trampolin') + A04 (file_metadata:
        # 'honeypot ... accesos ... bloqueado').
        assert block["surveillance_count"] == 2
        assert block["zero_contact_count"] >= 1
        assert block["penalty"] == "3/5"
