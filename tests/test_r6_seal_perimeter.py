"""
Test R6-1/R6-2/R6-3 — el perimetro del sello EBS.

R6-1 — CONFLICTO DE AUTORIDAD. `BundleBuilder.seal()` arma `bundle_payload`
desde una lista fija de claves, asi que todo campo agregado despues del sellado
queda FUERA del hash por construccion. El ledger de custodia sabia esto y
excluia `integrity`, `forensic_chain` y `pki` al recomputar. Los otros dos
verificadores recomputaban el payload como "todo menos integrity". Resultado
medido: un bundle producido por el propio `seal_with_chain()` de VIGIA — que
inyecta `forensic_chain` fuera del payload, por diseno documentado — era
declarado INTEGRO por el ledger y INVALIDO por `verify_ebs_v1.py` y
`quick_verify`. Dos componentes de VIGIA en desacuerdo sobre el mismo archivo
es lo peor que puede pasar en una pericia: la contraparte elige el que le
sirve. Lo mismo con `pki`: notarizar el bundle con un receipt RFC 3161 rompia
su propia verificacion.

R6-2 — ANCLAJE DEL AUDIT TRAIL. `tool_execution_log` no estaba cubierto por
`bundle_hash` y no podia estarlo: adjuntar CUALQUIER clave hermana a un bundle
sellado rompia el sello (medido). Fix: la PUNTA de la cadena
(`chain_tip_sha256` / `chain_tip_hmac`) entra dentro del payload sellado via
`seal(tool_log_tip=...)`, mientras el arreglo viaja como campo de presentacion.
Truncar el log rompe la comparacion contra el tip; reescribir el tip para
taparlo rompe `bundle_hash`, que a su vez esta anclado en el ledger con
checkpoint HMAC.

R6-3 — Borrar el log entero daba exit 2 ("NO_LOG — fallback/EBS bundle"): nadie
decia que faltaba algo que se habia sellado. Con el tip sellado, la ausencia es
detectable y se reporta como cadena rota.

LIMITE HONESTO, no cerrado: excluir `tool_execution_log` del hash abre un
vector que antes no existia — adjuntar un log FABRICADO a un bundle legitimo ya
no rompe el sello. Se reporta como `R1_SEAL_SCOPE` WARNING ("SIN ANCLA"), no
como ERROR, porque un log sin anclar no prueba que el bundle este alterado.
Promoverlo a ERROR es una decision para cuando todos los productores pasen
`tool_log_tip` a `seal()`. Medido en
`test_fabricated_log_without_anchor_is_reported`.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from vigia.core.bundle_builder import BundleBuilder
from vigia.core.ebs_v1 import (
    DecisionTrace, EvidenceGraph, ForensicBundle, SystemState, make_default_policy,
)
from vigia.core.tool_log_chain import ToolExecutionLogChain
from vigia.forensics.vigia_chain_of_custody import _declared_hash_mismatch

REPO_ROOT = Path(__file__).resolve().parent.parent
KEY = b"a" * 32
REAL_BUNDLE = REPO_ROOT / "vigia" / "results" / "OWL-COMPLETE_bundle_claude_fable.json"

FORENSIC_CHAIN = {
    "sequence": 1, "chain_hash": "ab" * 32, "previous_bundle_hash": "00" * 32,
    "chain_timestamp": "2026-09-11T00:00:00+00:00", "chain_version": "1.1",
}


def _real_bundle():
    if not REAL_BUNDLE.exists():
        pytest.skip("bundle EBS de referencia no presente")
    return json.loads(REAL_BUNDLE.read_text())


def _run_ebs(tmp_path, bundle, name="b.json"):
    path = tmp_path / name
    path.write_text(json.dumps(bundle, indent=2))
    return subprocess.run(
        [sys.executable, "forensics/verify_ebs_v1.py", str(path), "--verbose"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


def _sealed_with_log(n_entries: int = 3):
    """Bundle sellado con el tip de la cadena dentro del payload y el log
    adjunto como campo de presentacion."""
    chain = ToolExecutionLogChain(mode="claude_code", hmac_key=KEY)
    log = [
        chain.append(tool=t, target="/evidence/x", result_summary=s,
                     arguments={"t": t})
        for t, s in [("generate_forensic_hash", "SHA-256 ok"),
                     ("search_pattern", "12 hits: wevtutil cl"),
                     ("validate_and_correct_analysis", "VERDICT: MALICE")][:n_entries]
    ]
    fb = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["n1"], edges=[]),
        decision_trace=DecisionTrace(decision="REJECT", posterior=0.9,
                                     risk=0.8, drift_score=0.0),
        policy_spec=make_default_policy(),
        system_state=SystemState(drift_score=0.0, graph_stability_global=0.5),
    )
    sealed = BundleBuilder.seal(fb, tool_log_tip=chain.bundle_fields())
    sealed["tool_execution_log"] = log
    return sealed, log


class TestR6AuthorityConflict:
    """Los tres verificadores deben coincidir sobre el mismo archivo."""

    @pytest.mark.parametrize("field,value", [
        ("forensic_chain", FORENSIC_CHAIN),
        ("pki", {"rfc3161_receipt": "MIIB...", "signer": "HSM-01"}),
    ])
    def test_presentation_field_does_not_invalidate_the_seal(self, tmp_path, field, value):
        bundle = _real_bundle()
        assert BundleBuilder.quick_verify(bundle)[0], "el control ya no verifica"
        bundle[field] = value
        assert _run_ebs(tmp_path, bundle).returncode == 0
        assert BundleBuilder.quick_verify(bundle)[0]
        assert _declared_hash_mismatch(bundle) is None

    def test_all_three_verifiers_agree_on_tampering(self, tmp_path):
        """Control negativo: el fix no debe ablandar la deteccion."""
        bundle = _real_bundle()
        bundle["decision_trace"]["decision"] = "ACCEPT"
        assert _run_ebs(tmp_path, bundle).returncode == 1
        assert not BundleBuilder.quick_verify(bundle)[0]
        assert _declared_hash_mismatch(bundle) is not None

    def test_legacy_bundle_with_hashed_log_still_verifies(self, tmp_path):
        """Los bundles historicos hashean tool_execution_log DENTRO del payload.
        Excluirlo sin mas los rompia (medido sobre VIGIA-REAL-009)."""
        legacy = REPO_ROOT / "results" / "real" / "VIGIA-REAL-009_bundle.json"
        if not legacy.exists():
            pytest.skip("bundle legacy no presente")
        bundle = json.loads(legacy.read_text())
        assert "tool_execution_log" in bundle
        assert BundleBuilder.quick_verify(bundle)[0], "bundle legacy roto por R6-1"


class TestR6TipAnchoring:
    def test_tip_travels_inside_the_sealed_payload(self):
        sealed, _ = _sealed_with_log()
        assert sealed["chain_tip_sha256"]
        assert sealed["chain_tip_hmac"]
        assert BundleBuilder.quick_verify(sealed)[0]

    def test_attaching_the_log_does_not_break_the_seal(self, tmp_path):
        sealed, _ = _sealed_with_log()
        out = _run_ebs(tmp_path, sealed).stdout
        assert "[OK  ] R1_BUNDLE_HASH" in out, out
        assert "[OK  ] R1_SEAL_SCOPE" in out, out

    def _chain_exit(self, tmp_path, bundle):
        path = tmp_path / "c.json"
        path.write_text(json.dumps(bundle, indent=2))
        return subprocess.run(
            [sys.executable, "verify_tool_log.py", str(path),
             "--hmac-key-hex", KEY.hex()],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )

    def test_truncating_the_log_is_caught_by_the_sealed_tip(self, tmp_path):
        sealed, log = _sealed_with_log()
        sealed["tool_execution_log"] = log[:2]          # saca el veredicto MALICE
        assert self._chain_exit(tmp_path, sealed).returncode == 1

    def test_rewriting_the_tip_to_cover_it_breaks_the_seal(self, tmp_path):
        """El cierre: el atacante sin clave puede recomputar chain_tip_sha256,
        pero el tip esta DENTRO del payload sellado."""
        sealed, log = _sealed_with_log()
        sealed["tool_execution_log"] = log[:2]
        sealed["chain_tip_sha256"] = log[1]["entry_hash"]
        assert not BundleBuilder.quick_verify(sealed)[0]
        assert _run_ebs(tmp_path, sealed).returncode == 1
        assert self._chain_exit(tmp_path, sealed).returncode == 1

    def test_deleting_the_whole_log_is_reported_as_broken(self, tmp_path):
        """R6-3: antes daba exit 2 (NO_LOG) — ausencia silenciosa."""
        sealed, _ = _sealed_with_log()
        del sealed["tool_execution_log"]
        r = self._chain_exit(tmp_path, sealed)
        assert r.returncode == 1, r.stdout
        assert "el log fue borrado despues del sellado" in r.stdout


class TestR6UnanchoredLogIsReported:
    def test_fabricated_log_without_anchor_is_reported(self, tmp_path):
        """Limite honesto: excluir el log del hash permite adjuntar uno
        fabricado a un bundle legitimo. No rompe el sello — y por eso el
        verificador tiene que DECIRLO en vez de callarlo."""
        bundle = _real_bundle()
        bundle["tool_execution_log"] = [
            {"seq": 1, "tool": "FABRICADO", "result_summary": "todo limpio"}
        ]
        out = _run_ebs(tmp_path, bundle).stdout
        assert "[WARN] R1_SEAL_SCOPE" in out, out
        assert "SIN ANCLA" in out, out

    def test_clean_bundle_reports_full_coverage(self, tmp_path):
        out = _run_ebs(tmp_path, _real_bundle()).stdout
        assert "[OK  ] R1_SEAL_SCOPE" in out, out
        assert "cubre todo el archivo" in out, out


class TestR6PresentationLockstep:
    """Las tres copias de la lista de campos de presentacion deben coincidir.
    Mismo patron que tests/test_canonicalize_lockstep.py: las copias existen
    por diseno (verificadores stdlib-only), la divergencia es el bug."""

    def _const(self, path: Path, name: str):
        ns: dict = {}
        for line in path.read_text().splitlines():
            if line.startswith(f"{name} = ("):
                exec(line, ns)
                return ns[name]
        raise AssertionError(f"{name} no encontrado en {path}")

    def test_three_copies_agree(self):
        from vigia.core.bundle_builder import PRESENTATION_FIELDS
        ebs = self._const(REPO_ROOT / "forensics" / "verify_ebs_v1.py",
                          "_PRESENTATION_FIELDS")
        ledger = self._const(
            REPO_ROOT / "vigia" / "forensics" / "vigia_chain_of_custody.py",
            "_PRESENTATION_FIELDS")
        assert tuple(PRESENTATION_FIELDS) == tuple(ebs) == tuple(ledger)

    def test_legacy_hashed_fields_agree(self):
        from vigia.core.bundle_builder import _LEGACY_HASHED_FIELDS
        ebs = self._const(REPO_ROOT / "forensics" / "verify_ebs_v1.py",
                          "_LEGACY_HASHED_FIELDS")
        ledger = self._const(
            REPO_ROOT / "vigia" / "forensics" / "vigia_chain_of_custody.py",
            "_LEGACY_HASHED_FIELDS")
        assert tuple(_LEGACY_HASHED_FIELDS) == tuple(ebs) == tuple(ledger)
