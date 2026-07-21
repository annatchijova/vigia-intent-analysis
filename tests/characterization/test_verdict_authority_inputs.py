"""
tests/characterization/test_verdict_authority_inputs.py
=======================================================
CHARACTERIZATION test for the T cluster (docs/PATTERN_HUNT_20260718.md).
Generated 2026-07-18. This test DOES NOT JUDGE — it PINS the current behavior
of the verdict-authority inputs the deterministic core trusts verbatim from the
case JSON, so the doctrine decision (Anna's) is made against data, and any
future change to these channels is visible in the diff.

Three channels, each with verdict authority and NO validating runtime producer
(the L-062 pattern — an examiner-authored field the scorer trusts without
recomputing it against evidence):

  T-1 (L-063) — `caie_fractures` in CAIE-fallback mode. When live CAIE is
      importable the JSON fractures are RECOMPUTED and discarded
      (caie_fractures_source == "live_caie"). When CAIE is unavailable, a
      declared recognised CAIE fracture is preserved for review but has
      zero verdict authority: its boost is zero and the run abstains until CAIE
      can produce or reject it. An unrecognised type remains inert.

  T-2 (L-064) — `temporal_violations[].type == "STATISTICAL_UNIFORMITY"`. No
      runtime module emits it; only corpus-conversion scripts author it into
      case JSON. Read verbatim in ALL modes (not gated by CAIE availability):
      a fabricated entry adds sev*0.35 to the malice boost and flips
      NOISE -> SUSPICION.

  T-3 (L-065) — per-artifact `provenance_chain`. Only len() is consulted; the
      hash strings are NEVER recomputed or matched against artifact content.
      Two DIFFERENT sets of garbage hashes of the same length produce the same
      result (content is not checked); length alone moves the trust.

CONTRACT: these are pins, not endorsements. If the doctrine decision changes
any channel (validate the pair, add a producer, verify the hashes, cap the
verdict), THESE TESTS WILL FAIL — that is intended. Update the pin in the same
commit that changes the behavior, and cross-check L-063/064/065.

Run: PYTHONPATH=$(pwd) pytest tests/characterization/ -v --no-cov
"""
from __future__ import annotations

import builtins

import pytest

_scorer = pytest.importorskip(
    "vigia_scorer",
    reason="vigia_scorer not importable (run with PYTHONPATH=$(pwd))",
)
_vigia_score = _scorer._vigia_score


def _clean_case() -> dict:
    """Three low-score log artifacts: a NOISE baseline the channels perturb."""
    return {
        "case_id": "T-CHAR",
        "artifacts": [
            {
                "artifact_id": f"a{i}", "evidence_type": "log_entry",
                "source_tool": "read_evidence",
                "timestamp": f"2026-04-10T10:0{i}:00Z", "raw_score": 0.3,
                "prior_trust": 0.8, "provenance_chain": [f"sha256:c{i}"],
                "description": "log", "metadata": {},
            }
            for i in range(3)
        ],
        "temporal_violations": [], "caie_fractures": [],
        "expected_verdict": "UNKNOWN", "peirce_chain": {},
    }


# ---------------------------------------------------------------------------
# T-2 (L-064) — STATISTICAL_UNIFORMITY: phantom producer, all modes
# ---------------------------------------------------------------------------

class TestT2StatisticalUniformity:
    def test_clean_baseline_is_noise(self):
        r = _vigia_score(_clean_case())
        assert r["verdict"] == "NOISE", (
            f"baseline moved off NOISE ({r['verdict']}) — the T-2 pin needs a "
            "fresh low-score baseline"
        )

    def test_fabricated_su_flips_noise_to_suspicion(self):
        """PIN: a fabricated STATISTICAL_UNIFORMITY (no runtime producer) in the
        case JSON boosts malice and flips the verdict. If a validating producer
        or a gate lands, this pin moves."""
        case = _clean_case()
        case["temporal_violations"] = [{
            "type": "STATISTICAL_UNIFORMITY", "severity": 1.0,
            "cause": {"artifact_id": "a0"}, "effect": {"artifact_id": "a1"},
        }]
        r = _vigia_score(case)
        assert r["verdict"] == "SUSPICION", (
            "CHARACTERIZATION PIN MOVED (T-2): a fabricated STATISTICAL_UNIFORMITY "
            f"no longer flips NOISE->SUSPICION (got {r['verdict']}). If this is "
            "the L-064 doctrine fix, update the pin and the L-064 entry."
        )
        assert r.get("fracture_malice_boost", 0) > 0

    def test_su_fires_without_caie(self):
        """PIN: unlike caie_fractures, the SU boost is NOT gated by CAIE
        availability — it fires in fallback mode too."""
        case = _clean_case()
        case["temporal_violations"] = [{
            "type": "STATISTICAL_UNIFORMITY", "severity": 1.0,
            "cause": {"artifact_id": "a0"}, "effect": {"artifact_id": "a1"},
        }]
        _real = builtins.__import__

        def _block(name, *a, **k):
            if name.startswith("vigia.tools.caie"):
                raise ImportError("simulated CAIE unavailable")
            return _real(name, *a, **k)

        builtins.__import__ = _block
        try:
            r = _vigia_score(case)
        finally:
            builtins.__import__ = _real
        assert r.get("caie_fractures_source") == "json_fallback"
        assert r["verdict"] == "SUSPICION"


# ---------------------------------------------------------------------------
# T-1 (L-063) — declared caie_fractures have no authority in fallback mode
# ---------------------------------------------------------------------------

def _score_in_fallback(case: dict) -> dict:
    _real = builtins.__import__

    def _block(name, *a, **k):
        if name.startswith("vigia.tools.caie"):
            raise ImportError("simulated CAIE unavailable")
        return _real(name, *a, **k)

    builtins.__import__ = _block
    try:
        return _vigia_score(case)
    finally:
        builtins.__import__ = _real


def _one_artifact_case(fracture_type: str) -> dict:
    return {
        "case_id": "T1", "artifacts": [{
            "artifact_id": "a0", "evidence_type": "log_entry",
            "source_tool": "read_evidence", "timestamp": "2026-04-10T10:00:00Z",
            "raw_score": 0.2, "prior_trust": 0.8,
            "provenance_chain": ["sha256:c"], "description": "log", "metadata": {},
        }],
        "temporal_violations": [],
        "caie_fractures": [{
            "fracture_type": fracture_type, "severity": 0.95,
            "artifact_a": "x", "artifact_b": "y", "interpretation": "FABRICATED",
        }],
        "expected_verdict": "UNKNOWN", "peirce_chain": {},
    }


class TestT1FallbackFractureAuthority:
    def test_live_mode_ignores_json_fractures(self):
        """PIN: with live CAIE, JSON fractures are recomputed and discarded."""
        r = _vigia_score(_one_artifact_case("FALSE_FLAG_PATTERN"))
        assert r.get("caie_fractures_source") == "live_caie"
        assert r.get("caie_fracture_authority") == "live_caie"
        # The fabricated fracture does NOT drive the verdict in live mode.
        assert r["verdict"] == "NOISE"

    def test_fallback_recognised_type_is_retained_but_cannot_decide(self):
        """A JSON-only recognised fracture is disclosed, contributes no boost,
        and produces ABSTAIN until its named CAIE producer is available."""
        r = _score_in_fallback(_one_artifact_case("FALSE_FLAG_PATTERN"))
        assert r.get("caie_fractures_source") == "json_fallback"
        assert r["verdict"] == "ABSTAIN"
        assert r.get("fracture_malice_boost", 0) == 0
        assert r.get("caie_fracture_authority") == "unverified_json_no_verdict_authority"
        assert r.get("unverified_json_caie_fractures") == [
            _one_artifact_case("FALSE_FLAG_PATTERN")["caie_fractures"][0]
        ]
        # El veredicto previo ya no recibe el boost JSON artificial: el gate
        # transforma ese NOISE potencialmente falso-limpio en ABSTAIN.
        assert r.get("pre_unverified_caie_authority_verdict") == "NOISE"

    def test_fallback_unrecognised_type_is_inert(self):
        """PIN (bound): an UNRECOGNISED fracture type does nothing — the T-1
        exposure requires the attacker to know the recognised type set."""
        r = _score_in_fallback(_one_artifact_case("NOT_A_REAL_FRACTURE_TYPE"))
        assert r.get("caie_fractures_source") == "json_fallback"
        assert r.get("caie_fracture_authority") == "unverified_json_no_verdict_authority"
        assert r["verdict"] == "NOISE"
        assert r.get("fracture_malice_boost", 0) == 0

    def test_fallback_credibility_type_also_abstains(self):
        """A JSON-only CAIE declaration has no score authority in either
        direction: recognised credibility penalties cannot silently clean a
        case while their producer is unavailable."""
        r = _score_in_fallback(_one_artifact_case("VERDICT_CONFLICT"))
        assert r.get("caie_fractures_source") == "json_fallback"
        assert r["verdict"] == "ABSTAIN"
        assert r.get("fracture_malice_boost", 0) == 0
        assert r.get("fracture_credibility_penalty", 0) == 0


# ---------------------------------------------------------------------------
# T-3 (L-065) — provenance_chain: length only, hashes never verified
# ---------------------------------------------------------------------------

class TestT3ProvenanceChainNotVerified:
    def _case_with_chain(self, chain: list) -> dict:
        case = _clean_case()
        for a in case["artifacts"]:
            a["provenance_chain"] = list(chain)
        return case

    def test_hash_content_is_not_checked(self):
        """PIN: two DIFFERENT sets of garbage hashes of the SAME length produce
        the SAME score — the hash strings are never validated against content."""
        r1 = _vigia_score(self._case_with_chain(["deadbeef" * 8] * 5))
        r2 = _vigia_score(self._case_with_chain(["cafef00d" * 8] * 5))
        assert r1["score"] == r2["score"], (
            "CHARACTERIZATION PIN MOVED (T-3): provenance_chain content now "
            "affects the score — a hash-verification step may have landed "
            "(L-065). Update the pin."
        )

    def test_chain_length_alone_moves_trust(self):
        """PIN: length is the only thing consulted — a longer chain of garbage
        hashes changes mean_effective_trust with zero real hashes."""
        short = _vigia_score(self._case_with_chain(["x"]))
        long = _vigia_score(self._case_with_chain(["deadbeef" * 8] * 18))
        assert short.get("mean_effective_trust") != long.get("mean_effective_trust"), (
            "CHARACTERIZATION PIN MOVED (T-3): provenance_chain length no longer "
            "moves trust on its own. Update the pin and L-065."
        )
