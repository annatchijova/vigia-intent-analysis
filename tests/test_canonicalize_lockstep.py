"""
tests/test_canonicalize_lockstep.py
===================================
Lockstep guard for the canonical encoder copies (D3: signed-zero hardening).

The v1 canonical encoding (bool/int/float/str/None -> tagged strings, sorted
dict keys) is deliberately reimplemented in several places: the producer
(bundle_builder), the declared source of truth (vigia/core/canonicalize.py),
and the stdlib-only third-party verifiers, which by design import nothing from
the package. One input must produce one hash in every copy — a divergence
between producer and verifier is a broken seal, and a divergence between
verifier copies is a court-facing contradiction.

D3 hardening: the canonical form of every float zero is "0.00000000". IEEE-754
negative zero (-0.0) is normalized before formatting (obj + 0.0). This closed
the last gap of BUG-ENTROPY-001 / BUG-NLP-001 at the encoder layer: even if a
future module leaks -0.0 into a sealed payload, it can no longer split the
hash. Backward compatibility was verified empirically before the change: no
sealed bundle under results/ contains -0.0, so every historical hash verifies
unchanged, and CANONICALIZE_VERSION stays "1" (same number, same canon — a
clarification, not a schema change). Verifier scripts bumped to 1.3.0.

These tests load every reachable implementation — including the standalone
verifier scripts, by file path — and assert they stay in lockstep. If someone
edits one copy and not the others, this file fails.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from vigia.core.canonicalize import _canonicalize as canon_source_of_truth
from vigia.core.bundle_builder import (
    BundleBuilder,
    _canonicalize as canon_bundle_builder,
    _sha256_dict as sha_bundle_builder,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Standalone scripts (stdlib-only, __main__-guarded) loaded by file path.
#
# V-5 (docs/PATTERN_HUNT_20260718.md, 2026-07-18): the three test-dir copies of
# the verifier (tests/forensics/verify_ebs_v1.py, tests/integration/verify_ebs.py,
# tests/verify_ebs_v1_parcheado.py) were DELETED, not kept in lockstep. This
# file only guarded their _canonicalize; the rest of each copy rotted (the
# tests/forensics copy had already lost the R3-2 dual-canon fallback, so it
# would have REJECTED historical v1 bundles if ever run as a verifier, and
# tests/integration/verify_ebs.py was the pre-v1 version explicitly banned by
# scripts/pre_release_check.py). Nothing imported them as verifiers — every
# consumer (README, vigia/cli.py, integration tests, R3-2 CLI test) uses
# forensics/verify_ebs_v1.py. Deletion is the stronger lockstep: see
# TestRetiredCopiesStayDeleted below.
_SCRIPT_COPIES = {
    "forensics_verifier": "forensics/verify_ebs_v1.py",
    "tool_log_verifier": "verify_tool_log.py",
}

# Paths retired under V-5. A revival must consciously re-register the copy in
# _SCRIPT_COPIES (restoring the lockstep guard) — it cannot come back silently.
_RETIRED_COPIES = (
    "tests/forensics/verify_ebs_v1.py",
    "tests/integration/verify_ebs.py",
    "tests/verify_ebs_v1_parcheado.py",
)


def _load_script(rel_path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _all_impls():
    impls = {
        "core.canonicalize": canon_source_of_truth,
        "bundle_builder": canon_bundle_builder,
    }
    # models/ebs.py keeps a copy too (currently unimported elsewhere); keep it
    # in lockstep so a future revival cannot resurrect the divergence.
    ebs_models = pytest.importorskip("vigia.models.ebs")
    impls["models.ebs"] = ebs_models._canonicalize
    for name, rel in _SCRIPT_COPIES.items():
        impls[name] = _load_script(rel, f"lockstep_{name}")._canonicalize
    return impls


# A payload touching every type rule of the v1 schema, including both zeros.
MIXED_PAYLOAD = {
    "neg_zero": -0.0,
    "pos_zero": 0.0,
    "int_one": 1,
    "float_one": 1.0,
    "flag": True,
    "text": "x",
    "nothing": None,
    "nested": {"xs": [-0.0, 2, "y"], "inf": float("inf")},
}


class TestSignedZeroNormalization:
    def test_every_copy_normalizes_signed_zero(self):
        for name, fn in _all_impls().items():
            assert fn(-0.0) == "0.00000000" == fn(0.0), (
                f"{name}: canon(-0.0)={fn(-0.0)!r} must equal canon(0.0) — "
                f"signed zero split the seal (D3 hardening regressed)"
            )

    def test_all_copies_agree_on_mixed_payload(self):
        impls = _all_impls()
        reference = canon_source_of_truth(MIXED_PAYLOAD)
        for name, fn in impls.items():
            assert fn(MIXED_PAYLOAD) == reference, (
                f"{name} diverged from vigia/core/canonicalize.py on the mixed "
                f"payload — encoder copies are no longer in lockstep"
            )

    def test_v1_legacy_copies_agree(self):
        """R3-2: la ruta de compatibilidad (fallback a v1 para bundles
        historicos) tambien debe estar en lockstep — si una copia deriva su
        _canonicalize_v1, un bundle historico verificaria distinto segun quien
        lo verifique (contradiccion ante un tribunal)."""
        from vigia.core.canonicalize import _canonicalize_v1 as v1_source
        reference = v1_source(MIXED_PAYLOAD)
        impls = {
            "core.canonicalize": v1_source,
            "bundle_builder": pytest.importorskip("vigia.core.bundle_builder")._canonicalize_v1,
            "models.ebs": pytest.importorskip("vigia.models.ebs")._canonicalize_v1,
        }
        for name, rel in _SCRIPT_COPIES.items():
            mod = _load_script(rel, f"lockstep_v1_{name}")
            fn = getattr(mod, "_canonicalize_v1", None)
            if fn is not None:
                impls[name] = fn
        for name, fn in impls.items():
            assert fn(MIXED_PAYLOAD) == reference, (
                f"{name}._canonicalize_v1 diverged — la ruta de verificacion "
                f"de bundles historicos ya no esta en lockstep (R3-2)"
            )

    def test_v2_closes_string_scalar_collision(self):
        """R3-2 en el guard de lockstep: el default (v2) separa el string
        "true" del bool True en toda copia."""
        for name, fn in _all_impls().items():
            assert fn("true") != fn(True), f"{name}: colision True/'true' no cerrada (v2)"
            assert fn("1:int") != fn(1), f"{name}: colision 1/'1:int' no cerrada (v2)"

    def test_producer_and_authoritative_verifier_hash_identically(self):
        verifier = _load_script(
            _SCRIPT_COPIES["forensics_verifier"], "lockstep_hash_check"
        )
        assert sha_bundle_builder(MIXED_PAYLOAD) == verifier._sha256_dict(
            MIXED_PAYLOAD
        )

    def test_hash_of_negative_zero_equals_positive_zero(self):
        assert sha_bundle_builder({"e": -0.0}) == sha_bundle_builder({"e": 0.0})


class TestSealWithSignedZeroEndToEnd:
    def _seal(self, drift: float):
        from vigia.core.ebs_v1 import (
            DecisionTrace,
            EvidenceGraph,
            ForensicBundle,
            SystemState,
            make_default_policy,
        )

        bundle = ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=["n1"], edges=[]),
            decision_trace=DecisionTrace(
                decision="ABSTAIN", posterior=0.5, risk=0.1, drift_score=drift
            ),
            policy_spec=make_default_policy(),
            system_state=SystemState(drift_score=0.0, graph_stability_global=0.5),
        )
        return BundleBuilder.seal(bundle)

    def test_bundle_carrying_negative_zero_verifies(self):
        sealed = self._seal(-0.0)
        ok, msg = BundleBuilder.quick_verify(sealed)
        assert ok, msg

    def test_negative_and_positive_zero_seal_to_same_decision_hash(self):
        # The whole point of the hardening: the same number must not produce
        # two different sealed hashes depending on its IEEE sign bit.
        neg = self._seal(-0.0)["integrity"]["decision_hash"]
        pos = self._seal(0.0)["integrity"]["decision_hash"]
        assert neg == pos


class TestUnreachableCopiesSourceTripwire:
    """
    Two copies cannot be exercised through imports: the chain_of_custody CLI
    fallback only exists when the package import fails (impossible inside this
    suite). A source-text tripwire is honest second-best: it fails if someone
    reverts the hardening in that copy without touching the others.
    """

    def test_chain_of_custody_fallback_is_hardened(self):
        src = (REPO_ROOT / "vigia/forensics/vigia_chain_of_custody.py").read_text(
            encoding="utf-8"
        )
        assert 'f"{obj + 0.0:.8f}"' in src
        assert 'f"{obj:.8f}"' not in src


class TestRetiredCopiesStayDeleted:
    """V-5: a stale verifier copy is a court-facing contradiction waiting to
    happen (the tests/forensics copy had already diverged semantically). The
    copies were deleted; this tripwire keeps them deleted. If one reappears,
    either delete it again or re-register it in _SCRIPT_COPIES so the
    lockstep guard covers it — never both absent."""

    @pytest.mark.parametrize("rel", _RETIRED_COPIES)
    def test_retired_copy_absent_or_registered(self, rel):
        path = REPO_ROOT / rel
        if path.exists():
            assert rel in _SCRIPT_COPIES.values(), (
                f"{rel} reappeared WITHOUT re-registering in _SCRIPT_COPIES — "
                "an unguarded verifier copy can drift silently (V-5, "
                "docs/PATTERN_HUNT_20260718.md). Delete it or register it."
            )
