"""
F2 (L-029) — cross-bundle pairing as architecture, ZERO verdict authority
(tests written RED first).

Contract (dossier §5-F2 + Kimi's audit §6):

  A. `vigia.tools.paired_review.compare_paired_bundles(path_a, path_b)`:
     deterministic sub-metrics only — case_origin equality read from
     artifacts[].metadata (Kimi's trap: top-level case_origin is None in
     every KIWI file), Fraction prior_trust delta (the 0.3-vs-0.8
     asymmetry IS the L-029 signal), detect_darvo_pattern over the
     artifact union, provenance overlap/disjunction — plus a mandatory
     adversarial caveat block in the output itself. Label-blind: the
     result must be identical with expected_verdict stripped. The
     Thirdness reasoning belongs to the calling analyst/LLM (Mode 2),
     OUTSIDE the decision loop.

  B. `vigia.core.case_linkage.emit_linkage_records(case_paths)`:
     deterministic group records keyed on the artifact-metadata
     case_origin, with copy-dedup (KIWI-004/005 are artifact-identical to
     003 — without dedup one expediente would emit multiple linkages, the
     L-016 violation judge 12 flagged), artifact_id collision caveats
     (RT-FN-COLLUSION-001 reuses KIWI-006 ids with the same case_origin —
     the forged-join-key attack that already exists in-repo, permanent
     fixture), label-blindness, and an HMAC seal over the canonical
     record when VIGIA_HMAC_KEY is set. Linkage records carry NO verdict
     authority — the caveats say so in the record itself.
"""

import copy
import hashlib
import hmac as hmac_mod
import json
from fractions import Fraction
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CASES = REPO / "data" / "cases"


# ── A. compare_paired_bundles ──────────────────────────────────────────────


class TestComparePairedBundles:
    def _run(self):
        from vigia.tools.paired_review import compare_paired_bundles
        return compare_paired_bundles(
            str(CASES / "VIGIA_KIWI_002_ZAPALLO_POV.json"),
            str(CASES / "VIGIA_KIWI_003_AT_POV.json"),
        )

    def test_case_origin_from_artifact_metadata(self):
        r = self._run()
        assert r["case_origin"]["a"] == "MPF7779408"
        assert r["case_origin"]["b"] == "MPF7779408"
        assert r["case_origin"]["match"] is True

    def test_prior_trust_asymmetry_as_fractions(self):
        r = self._run()
        assert Fraction(r["prior_trust"]["mean_a"]) == Fraction(3, 10)
        assert Fraction(r["prior_trust"]["mean_b"]) == Fraction(4, 5)
        assert Fraction(r["prior_trust"]["delta"]) == Fraction(1, 2)

    def test_darvo_union_detects_the_inversion_evidence(self):
        # The union carries KIWI-003's verified surveillance artifacts, so
        # the pattern fires on the union even though KIWI-002 alone is
        # blind — this is exactly the pairing value.
        r = self._run()
        assert r["darvo_union"]["pattern_present"] is True

    def test_framing_complement_detected(self):
        r = self._run()
        assert r["framing"] == {"a": "perspective_actor_a",
                                "b": "perspective_actor_b",
                                "complementary": True}

    def test_mandatory_adversarial_caveats(self):
        r = self._run()
        caveats = " ".join(r["caveats"]).lower()
        assert "verdict" in caveats          # no verdict authority
        assert "examiner" in caveats         # keys are examiner-authored
        assert "l-004" in caveats
        assert r["verdict_authority"] == "none"

    def test_label_blind(self):
        from vigia.tools.paired_review import compare_paired_bundles_data
        a = json.loads((CASES / "VIGIA_KIWI_002_ZAPALLO_POV.json").read_text(
            encoding="utf-8"))
        b = json.loads((CASES / "VIGIA_KIWI_003_AT_POV.json").read_text(
            encoding="utf-8"))
        full = compare_paired_bundles_data(a, b)
        for d in (a, b):
            d.pop("expected_verdict", None)
        stripped = compare_paired_bundles_data(a, b)
        assert full == stripped


# ── B. case linkage records ────────────────────────────────────────────────


def _kiwi_paths():
    return sorted(CASES.glob("VIGIA_KIWI_*.json"))


class TestLinkageRecords:
    def test_one_record_for_the_kiwi_group_with_copy_dedup(self):
        from vigia.core.case_linkage import emit_linkage_records
        records = emit_linkage_records(_kiwi_paths())
        assert len(records) == 1
        rec = records[0]
        assert rec["case_origin"] == "MPF7779408"
        stems = {m["stem"] for m in rec["members"]}
        # 004/005 are artifact-identical to 003: they are COPIES, not
        # members — without this rule one expediente emits multiple
        # linkages against duplicated evidence (L-016).
        assert "VIGIA_KIWI_004_ADV_CULPABILIDAD" not in stems
        assert "VIGIA_KIWI_005_ADV_INOCENCIA" not in stems
        copies = {c["stem"] for c in rec["copies"]}
        assert copies == {"VIGIA_KIWI_004_ADV_CULPABILIDAD",
                          "VIGIA_KIWI_005_ADV_INOCENCIA"}
        assert rec["verdict_authority"] == "none"

    def test_primary_complementary_pair_identified(self):
        from vigia.core.case_linkage import emit_linkage_records
        rec = emit_linkage_records(_kiwi_paths())[0]
        pair = rec["primary_pair"]
        assert pair["actor_a_pov"] == "VIGIA_KIWI_002_ZAPALLO_POV"
        assert pair["actor_b_pov"] == "VIGIA_KIWI_003_AT_POV"

    def test_rt_collusion_fixture_raises_collision_caveat(self):
        # The forged-join-key attack already exists in-repo: RT-FN-
        # COLLUSION-001 carries case_origin MPF7779408 and reuses
        # KIWI-006's artifact_ids verbatim. Including it must produce a
        # collision caveat, never certify cleanliness.
        from vigia.core.case_linkage import emit_linkage_records
        rt = CASES / "red-team" / "RT-FN-COLLUSION-001.json"
        assert rt.exists(), "permanent fixture missing"
        records = emit_linkage_records(_kiwi_paths() + [rt])
        rec = next(r for r in records if r["case_origin"] == "MPF7779408")
        assert any("collision" in c.lower() for c in rec["caveats"]), (
            "reused artifact_ids across distinct case files must be flagged"
        )

    def test_label_blind(self):
        from vigia.core.case_linkage import emit_linkage_records_data
        datas = []
        for p in _kiwi_paths():
            datas.append((p.stem, json.loads(p.read_text(encoding="utf-8"))))
        full = emit_linkage_records_data(datas)
        stripped_datas = []
        for stem, d in datas:
            d2 = copy.deepcopy(d)
            d2.pop("expected_verdict", None)
            stripped_datas.append((stem, d2))
        assert full == emit_linkage_records_data(stripped_datas)

    def test_hmac_seal_when_key_present(self, monkeypatch):
        from vigia.core.case_linkage import emit_linkage_records
        key = "f0" * 16
        monkeypatch.setenv("VIGIA_HMAC_KEY", key)
        monkeypatch.delenv("VIGIA_HMAC_KEY_FILE", raising=False)
        rec = emit_linkage_records(_kiwi_paths())[0]
        assert rec["record_sha256"]
        expected = hmac_mod.new(
            key.encode(), rec["record_sha256"].encode(), hashlib.sha256
        ).hexdigest()
        assert rec["record_hmac"] == expected

    def test_deterministic_across_runs(self):
        from vigia.core.case_linkage import emit_linkage_records
        r1 = emit_linkage_records(_kiwi_paths())
        r2 = emit_linkage_records(list(reversed(_kiwi_paths())))
        assert r1 == r2, "records must be order-independent and timestamp-free"
