"""
Test R5-1/R5-2/R5-3 — degradacion de esquema en el verificador standalone.

Surprise / expectation violated: R3-2 hizo tamper-evident cada campo de cada
entrada (entry_hash), A3 agrego entry_hmac para que una cadena recomputada sin
la clave sea detectable, y R3-5 anclo la cola con chain_tip_sha256 /
chain_tip_hmac. Las tres defensas viven en la via v2 de verify_tool_log.py.
Pero la via se elegia asi:

    version = "2" if log[0].get("entry_hash") else "1"

es decir: un unico campo borrable, dentro del arreglo que el atacante edita,
seleccionaba el ALGORITMO DE VERIFICACION. Borrando `entry_hash` de la primera
entrada la cadena se validaba por la via v1 — que no cubre timestamp/tool/
target/input_hash, NO recibe la clave HMAC (`_verify_v1` no tenia parametro de
clave) y NO mira chain_tip_sha256. Las tres defensas se apagaban juntas, sin
que el atacante necesitara la clave, y el verificador imprimia
"CHAIN VERIFIED" con exit 0.

Es el patron clasico de downgrade de suite criptografica: el dato no
autenticado negocia el algoritmo que deberia autenticarlo.

Fix (R5-1): `_detect_schema` deduce el esquema de TODOS los marcadores v2
(chain_version="2" / entry_hash / entry_hmac en cualquier entrada;
chain_tip_sha256 / chain_tip_hmac a nivel bundle). Si algo declara v2 se
verifica como v2, y a la entrada sin entry_hash se la reporta como contenido
alterado — que es lo que es. Con clave provista, un log v1 se reporta como
degradacion salvo --allow-legacy-v1.

Fix (R5-2): borrar chain_tip_sha256/chain_tip_hmac de un bundle cuyas entradas
llevan entry_hmac es un borrado, no un bundle viejo — `bundle_fields()` emite
ancla y HMAC de punta juntos siempre que hay clave. Sin ese chequeo, borrar el
ancla devolvia la truncacion de cola a ser indetectable incluso con la clave.

Limite honesto (no se sobre-declara): un atacante que borre TODOS los
marcadores v2 produce un bundle indistinguible de uno legacy v1 genuino
cuando el verificador corre SIN clave. Con clave, R5-1 lo marca. Ese residual
queda medido en test_full_marker_strip_is_flagged_only_when_keyed.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from vigia.core.tool_log_chain import ToolExecutionLogChain

REPO_ROOT = Path(__file__).resolve().parent.parent
KEY = b"a" * 32
KEY_HEX = KEY.hex()


def _keyed_bundle(n: int = 4) -> dict:
    """Bundle v2 sellado CON clave: entry_hmac + chain_tip_sha256 + tip_hmac."""
    chain = ToolExecutionLogChain(mode="claude_code", hmac_key=KEY)
    log = [
        chain.append(tool=f"tool_{seq}", target=f"/evidence/art_{seq}",
                     result_summary=("VERDICT: MALICE | anti-forensics" if seq == n
                                     else f"resultado {seq}"),
                     arguments={"seq": seq})
        for seq in range(1, n + 1)
    ]
    return {"case_id": "CASE-R5", "tool_execution_log": log, **chain.bundle_fields()}


def _downgrade_to_v1(bundle: dict, drop_chain_version: bool = False) -> dict:
    """Reescribe el log con el esquema v1: sin entry_hash/entry_hmac y con
    prev_hash = SHA-256(result_summary anterior), "GENESIS" en seq=1."""
    out = copy.deepcopy(bundle)
    prev = None
    for entry in out["tool_execution_log"]:
        entry.pop("entry_hash", None)
        entry.pop("entry_hmac", None)
        if drop_chain_version:
            entry.pop("chain_version", None)
            out.pop("chain_tip_sha256", None)
            out.pop("chain_tip_hmac", None)
        entry["prev_hash"] = ("GENESIS" if prev is None
                              else hashlib.sha256(prev.encode()).hexdigest())
        prev = entry["result_summary"]
    return out


def _run(tmp_path, bundle, *extra, keyed: bool = True):
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(bundle))
    cmd = [sys.executable, "verify_tool_log.py", str(path), *extra]
    if keyed:
        cmd += ["--hmac-key-hex", KEY_HEX]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


class TestR5SchemaDowngrade:
    def test_control_keyed_bundle_verifies(self, tmp_path):
        r = _run(tmp_path, _keyed_bundle())
        assert r.returncode == 0, r.stdout
        assert "CHAIN VERIFIED" in r.stdout
        assert "Schema : chain v2" in r.stdout

    def test_control_tamper_under_v2_is_caught(self, tmp_path):
        """Sanity: sin degradar el esquema, alterar un veredicto rompe."""
        bundle = _keyed_bundle()
        bundle["tool_execution_log"][-1]["result_summary"] = "VERDICT: NOISE"
        r = _run(tmp_path, bundle)
        assert r.returncode == 1, r.stdout
        assert "CHAIN BROKEN" in r.stdout

    def test_downgrade_with_tamper_is_caught(self, tmp_path):
        """R5-1: MALICE -> NOISE reescrito bajo el esquema v1, con la clave en
        mano. Antes del fix: exit 0, "CHAIN VERIFIED (schema v1)"."""
        bundle = _keyed_bundle()
        bundle["tool_execution_log"][-1]["result_summary"] = "VERDICT: NOISE"
        bundle["tool_execution_log"][1]["target"] = "/evidence/otra_cosa"
        r = _run(tmp_path, _downgrade_to_v1(bundle))
        assert r.returncode == 1, r.stdout
        assert "Schema : chain v2" in r.stdout, "el bundle declara v2: no debe caer a v1"
        assert "CHAIN BROKEN" in r.stdout

    def test_downgrade_ignores_the_tail_anchor(self, tmp_path):
        """R5-1: bajo v1 el ancla de cola ni se miraba, aunque estuviera
        presente y quedara obsoleta."""
        bundle = _keyed_bundle()
        bundle["tool_execution_log"][-1]["result_summary"] = "VERDICT: NOISE"
        downgraded = _downgrade_to_v1(bundle)   # chain_tip_* intactos y stale
        assert "chain_tip_sha256" in downgraded
        r = _run(tmp_path, downgraded)
        assert r.returncode == 1, r.stdout
        assert "Schema : chain v2" in r.stdout

    def test_single_entry_marker_forces_v2(self, tmp_path):
        """El marcador de UNA sola entrada basta: borrar entry_hash de la
        primera entrada ya no elige el algoritmo."""
        bundle = _keyed_bundle()
        del bundle["tool_execution_log"][0]["entry_hash"]
        r = _run(tmp_path, bundle)
        assert r.returncode == 1, r.stdout
        assert "Schema : chain v2" in r.stdout

    def test_full_marker_strip_is_flagged_only_when_keyed(self, tmp_path):
        """Residual honesto: sin ningun marcador v2, el bundle es
        indistinguible de uno legacy. Con clave se reporta como degradacion;
        sin clave pasa como v1 (limite documentado, no cerrado)."""
        stripped = _downgrade_to_v1(_keyed_bundle(), drop_chain_version=True)
        keyed = _run(tmp_path, stripped)
        assert keyed.returncode == 1, keyed.stdout
        assert "DEGRADACION" in keyed.stdout

        unkeyed = _run(tmp_path, stripped, keyed=False)
        assert unkeyed.returncode == 0, unkeyed.stdout
        assert "Schema : chain v1" in unkeyed.stdout

    def test_allow_legacy_v1_escape_hatch(self, tmp_path):
        """Bundles historicos genuinos siguen verificables con clave en el
        entorno, de forma explicita."""
        stripped = _downgrade_to_v1(_keyed_bundle(), drop_chain_version=True)
        r = _run(tmp_path, stripped, "--allow-legacy-v1")
        assert r.returncode == 0, r.stdout
        assert "CAVEAT v1" in r.stdout


class TestR5AnchorStripping:
    def test_tail_truncation_with_anchor_stripped_is_caught(self, tmp_path):
        """R5-2: truncar la cola y borrar el ancla. Antes del fix: exit 0
        incluso con la clave provista."""
        bundle = _keyed_bundle()
        bundle["tool_execution_log"] = bundle["tool_execution_log"][:2]
        bundle.pop("chain_tip_sha256"), bundle.pop("chain_tip_hmac")
        r = _run(tmp_path, bundle)
        assert r.returncode == 1, r.stdout
        assert "chain_tip_sha256 ausente" in r.stdout

    def test_tip_hmac_stripped_is_caught(self, tmp_path):
        """R5-2: borrar solo chain_tip_hmac deja el ancla recomputable."""
        bundle = _keyed_bundle()
        bundle.pop("chain_tip_hmac")
        r = _run(tmp_path, bundle)
        assert r.returncode == 1, r.stdout
        assert "chain_tip_hmac ausente" in r.stdout

    def test_unkeyed_bundle_without_anchor_still_only_a_note(self, tmp_path):
        """Contrato R3-5 preservado: sin entry_hmac, la ausencia de ancla es
        retrocompatibilidad (bundle viejo), no un fallo."""
        chain = ToolExecutionLogChain(mode="claude_code", use_env_key=False)
        log = [chain.append(tool="t", target="x", result_summary="r",
                            arguments={"i": i}) for i in range(3)]
        r = _run(tmp_path, {"tool_execution_log": log}, keyed=False)
        assert r.returncode == 0, r.stdout
        assert "Sin chain_tip_sha256" in r.stdout


class TestR5MalformedLog:
    """R5-3 (hygiene): un log malformado da diagnostico, no traceback."""

    def test_non_dict_entry(self, tmp_path):
        r = _run(tmp_path, {"tool_execution_log": ["no soy un objeto"]}, keyed=False)
        assert r.returncode == 1
        assert "entradas malformadas" in r.stdout
        assert "Traceback" not in r.stderr

    def test_log_is_not_a_list(self, tmp_path):
        r = _run(tmp_path, {"tool_execution_log": {"seq": 1}}, keyed=False)
        assert r.returncode == 1
        assert "debe ser una lista" in r.stdout
        assert "Traceback" not in r.stderr
