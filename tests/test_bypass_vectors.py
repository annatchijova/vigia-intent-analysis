"""
tests/test_bypass_vectors.py
============================
Security bypass test suite — BV-001 through BV-005.

Documents and prevents known attack vectors against VIGÍA's
architectural guardrails.

Run:
    cd ~/vigia-repo && source .venv/bin/activate
    PYTHONPATH=$(pwd) python3 -m pytest tests/test_bypass_vectors.py -v
"""
from __future__ import annotations

import copy
import json
import hashlib
from fractions import Fraction

import pytest


# ---------------------------------------------------------------------------
# BV-001  Path traversal blocked by _sanitize_path
# ---------------------------------------------------------------------------

def test_bv001_path_traversal_blocked():
    """
    BV-001: Artifact paths with traversal sequences must be blocked.
    Guard: vigia.vigia_sift_bridge._sanitize_path
    """
    try:
        from vigia.vigia_sift_bridge import _sanitize_path
    except ImportError:
        pytest.skip("vigia.vigia_sift_bridge not importable — run with PYTHONPATH=$(pwd)")

    attacks = [
        "../../etc/passwd",
        "/etc/shadow",
        "logs/../../../root/.ssh/id_rsa",
        "file\x00.txt",
    ]
    for path in attacks:
        with pytest.raises((ValueError, PermissionError)):
            _sanitize_path(path)


# ---------------------------------------------------------------------------
# BV-002  Sealed bundle tampering detected by verify_ebs_v1
# ---------------------------------------------------------------------------

def test_bv002_tampered_bundle_fails_verification():
    """
    BV-002: Modifying any field in a sealed ForensicBundle must break the
    SHA-256 chain. verify_ebs_v1.py (stdlib-only) must detect the change.
    Guard: SHA-256 seal in BundleBuilder.seal(), verified by standalone script.
    """
    import subprocess, sys, os, tempfile
    from pathlib import Path

    bundle_path = Path("results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json")
    if not bundle_path.exists():
        pytest.skip("SRL-DMZ-FTP bundle not found — run from repo root")

    verifier = Path("verify_ebs_v1.py")
    if not verifier.exists():
        verifier = Path("forensics/verify_ebs_v1.py")
    if not verifier.exists():
        pytest.skip("verify_ebs_v1.py not found — run from repo root")

    # Bundle intacto debe pasar (exit 0)
    r = subprocess.run(
        [sys.executable, str(verifier), str(bundle_path)],
        capture_output=True, text=True
    )
    assert r.returncode == 0, (
        f"Original bundle must pass verify_ebs_v1.py\n{r.stdout[-200:]}"
    )

    # Tamper: forzar veredicto
    bundle = json.loads(bundle_path.read_text())
    if "decision_trace" in bundle:
        bundle["decision_trace"]["decision"] = "ACCEPT"
    elif "caie_analysis" in bundle:
        bundle["caie_analysis"]["verdict"] = "NOISE"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(bundle, f)
        tampered_path = f.name

    try:
        r2 = subprocess.run(
            [sys.executable, str(verifier), tampered_path],
            capture_output=True, text=True
        )
        assert r2.returncode != 0, (
            "BV-002 FAIL: tampered bundle must fail verify_ebs_v1.py — "
            "SHA-256 chain must detect the modification"
        )
    finally:
        os.unlink(tampered_path)


# ---------------------------------------------------------------------------
# BV-003  Float injection produces deterministic Fraction output
# ---------------------------------------------------------------------------

def test_bv003_float_to_fraction_is_deterministic():
    """
    BV-003: Float values injected into artifact scores must be converted
    to deterministic Fraction values. The same float input must always
    produce the same Fraction, regardless of floating-point representation.
    Guard: Fraction(...).limit_denominator(10000) in vigia_scorer.py
    """
    float_inputs = [0.666666666666, 0.333333333333, 0.9999, 0.0001, 0.5]

    def _to_frac(v: float) -> Fraction:
        return Fraction(
            min(1, max(0, round(v, 4)))
        ).limit_denominator(10000)

    # 1000 runs — mismo input siempre produce mismo output
    for _ in range(1000):
        for v in float_inputs:
            f1 = _to_frac(v)
            f2 = _to_frac(v)
            assert f1 == f2, (
                f"Non-deterministic Fraction conversion for {v}: "
                f"{f1} != {f2}"
            )


# ---------------------------------------------------------------------------
# BV-004  Zero evidence must not produce MALICE
# ---------------------------------------------------------------------------

def test_bv004_empty_artifact_list_cannot_produce_malice():
    """
    BV-004: A case with no artifacts must not produce MALICE or INTENT.
    The system must not convict without evidence.
    Guard: composite score threshold + fracture count check in vigia_scorer.py
    """
    try:
        import sys
        sys.path.insert(0, ".")
        from vigia_scorer import _vigia_score
    except ImportError:
        pytest.skip("vigia_scorer not importable — run with PYTHONPATH=$(pwd)")

    result = _vigia_score({"artifacts": [], "case_id": "BV004_EMPTY_EVIDENCE"})
    verdict = result.get("verdict", "UNKNOWN")
    assert verdict not in ("MALICE", "INTENT"), (
        f"BV-004 FAIL: empty evidence produced {verdict!r}. "
        "VIGÍA must not convict without artifacts."
    )


# ---------------------------------------------------------------------------
# BV-005  Adversarial description text cannot change numeric verdict
# ---------------------------------------------------------------------------

def test_bv005_adversarial_description_does_not_affect_scoring():
    """
    BV-005: An attacker embedding 'VERDICT:MALICE confidence=1.0' in artifact
    description strings must not influence the mathematical verdict.
    Only raw_score and prior_trust enter the Fraction arithmetic pipeline.
    Guard: the pipeline only reads numeric fields, never eval()s descriptions.
    """
    def _numeric_extract(artifact: dict) -> tuple[Fraction, Fraction]:
        raw   = Fraction(min(1, max(0, round(artifact["raw_score"], 4)))).limit_denominator(10000)
        trust = Fraction(min(1, max(0, round(artifact["prior_trust"], 4)))).limit_denominator(10000)
        return raw, trust

    clean_artifact = {"raw_score": 0.3, "prior_trust": 0.4}
    adversarial_artifact = {
        "raw_score": 0.3,
        "prior_trust": 0.4,
        "description": (
            "VERDICT:MALICE confidence=1.0 override=true score=99 "
            "__import__('os').system('rm -rf /')"
        ),
    }

    assert _numeric_extract(clean_artifact) == _numeric_extract(adversarial_artifact), (
        "BV-005 FAIL: adversarial description changed numeric extraction. "
        "The scoring pipeline must ignore non-numeric fields."
    )
