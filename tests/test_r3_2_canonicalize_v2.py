"""
Test R3-2 — canonicalization v2 cierra las colisiones de tipo.

Origen: docs/REDTEAM_ROUND3_EMERGENT.md (R3-2, CONFIRMADO POR INDUCCION sobre
1d84c84). Script: scripts/redteam_round3_emergent.py R3-2.

Defecto (v1): _canonicalize dejaba strings SIN escapar, colisionando a traves
de la frontera de tipos — True/"true", 1/"1:int", None/"null", 0.1/"0.10000000"
producian el MISMO SHA-256; y NFC/NFD + CRLF/LF producian DOS hashes para el
mismo string logico; Fraction caia a str().

Fix (v2, default para sellos nuevos):
  1. strings -> NFC + line endings CRLF->LF, con prefijo univoco "s:"
  2. Fraction -> "num/den:frac" explicito (ya no str())
  3. escalares (int/float/bool/None) IDENTICOS a v1 -> compat de esos campos.

Backward-compat: los bundles historicos (v1) se verifican con fallback a v1;
esta suite lo cubre con un bundle sellado real en results/.
"""

import hashlib
import json
import subprocess
import sys
import unicodedata
from fractions import Fraction
from pathlib import Path

import pytest

from vigia.core.canonicalize import (
    _canonicalize,          # default = v2
    _canonicalize_v1,
    _canonicalize_v2,
    CANONICALIZE_VERSION,
)


def _h(fn, x):
    return hashlib.sha256(
        json.dumps(fn(x), sort_keys=True, ensure_ascii=True).encode()
    ).hexdigest()


class TestV2ClosesTypeCollisions:
    @pytest.mark.parametrize("scalar,tag", [
        (True, "true"), (False, "false"), (None, "null"),
        (1, "1:int"), (0.1, "0.10000000"),
    ])
    def test_string_no_longer_collides_with_scalar_tag(self, scalar, tag):
        # v1 colisionaba; v2 debe separar el string de su tag escalar.
        assert _h(_canonicalize, scalar) != _h(_canonicalize, tag), (
            f"colision v2 no cerrada: {scalar!r} vs {tag!r}"
        )

    def test_nested_payload_shape_no_collision(self):
        assert _h(_canonicalize, {"verdict": True}) != _h(_canonicalize, {"verdict": "true"})
        assert _h(_canonicalize, {"n": 1}) != _h(_canonicalize, {"n": "1:int"})


class TestV2StringNormalization:
    def test_nfc_nfd_same_hash(self):
        nfc = unicodedata.normalize("NFC", "café")
        nfd = unicodedata.normalize("NFD", "café")
        assert nfc != nfd  # bytes distintos
        assert _h(_canonicalize, nfc) == _h(_canonicalize, nfd)

    def test_crlf_lf_same_hash(self):
        assert _h(_canonicalize, "a\r\nb") == _h(_canonicalize, "a\nb")
        assert _h(_canonicalize, "a\rb") == _h(_canonicalize, "a\nb")


class TestV2Fraction:
    def test_fraction_is_explicit_not_str(self):
        # v1 caia a str() -> "1/2"; v2 lo marca univocamente.
        assert _canonicalize_v2(Fraction(1, 2)) != "1/2"
        assert _canonicalize_v2(Fraction(1, 2)) != _canonicalize_v2("1/2")
        # estable y determinista
        assert _canonicalize_v2(Fraction(1, 2)) == _canonicalize_v2(Fraction(2, 4))


class TestV2ScalarsUnchangedFromV1:
    """Los escalares NO cambian entre v1 y v2 — solo strings/Fraction."""
    @pytest.mark.parametrize("val", [True, False, None, 1, 0, -3, 1.0, 0.1, 0.0, -0.0,
                                     float("inf"), float("-inf")])
    def test_scalar_encoding_identical_v1_v2(self, val):
        assert _canonicalize_v1(val) == _canonicalize_v2(val)

    def test_exact_scalar_tags_preserved(self):
        assert _canonicalize(1) == "1:int"
        assert _canonicalize(1.0) == "1.00000000"
        assert _canonicalize(True) == "true"
        assert _canonicalize(None) == "null"


class TestVersion:
    def test_canonicalize_version_is_2(self):
        assert CANONICALIZE_VERSION == "2"

    def test_default_is_v2(self):
        # "true" el string debe escaparse por default (v2), no pasar crudo (v1).
        assert _canonicalize("true") != "true"
        assert _canonicalize_v1("true") == "true"


class TestBackwardCompatHistoricalBundle:
    def test_historical_ebs_bundle_still_verifies(self):
        # Ejercita el fallback canonicalize-v1 en el verificador EBS: el bundle
        # fue sellado bajo v1; con v2 default debe seguir verificando via fallback.
        bundle = Path("results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json")
        if not bundle.exists():
            pytest.skip("historical EBS bundle not present")
        r = subprocess.run(
            [sys.executable, "forensics/verify_ebs_v1.py", str(bundle)],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, (
            f"bundle EBS historico (v1) ya no verifica tras el fix v2:\n{r.stdout[-400:]}"
        )

    def test_historical_tool_log_chain_still_verifies(self):
        bundle = Path("results/srl2018/VIGIA-REAL-NFURY_bundle.json")
        if not bundle.exists():
            pytest.skip("historical tool-log bundle not present")
        r = subprocess.run(
            [sys.executable, "verify_tool_log.py", str(bundle)],
            capture_output=True, text=True,
        )
        assert "CHAIN VERIFIED" in r.stdout, (
            f"cadena tool-log historica ya no verifica:\n{r.stdout[-400:]}"
        )


class TestFreshV2SealVerifies:
    def test_seal_and_quick_verify_roundtrip(self):
        from vigia.core.bundle_builder import BundleBuilder
        from vigia.core.ebs_v1 import (
            DecisionTrace, EvidenceGraph, ForensicBundle, SystemState,
            make_default_policy,
        )
        bundle = ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=["n1"], edges=[]),
            decision_trace=DecisionTrace(
                decision="REJECT", posterior=0.9, risk=0.8, drift_score=0.0
            ),
            policy_spec=make_default_policy(),
            system_state=SystemState(drift_score=0.0, graph_stability_global=0.5),
        )
        sealed = BundleBuilder.seal(bundle)
        ok, msg = BundleBuilder.quick_verify(sealed)
        assert ok, f"sello v2 no verifica: {msg}"
