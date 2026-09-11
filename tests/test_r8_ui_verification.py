"""
Test R8-1/R8-2 — la web UI como superficie de verificacion.

La UI esta bien arquitecturada en lo grande: invoca los verificadores reales
como subprocesos stdlib-only y nunca los importa ni anula su exit code, asi que
no reintroduce el conflicto de autoridad de R6-1. Los dos defectos estan en los
bordes de esa arquitectura.

R8-1 — La clave HMAC que el usuario pega en la web viajaba por ARGV del
subproceso. El comentario del codigo decia "passed as argv, never logged and
never echoed back in the response": la segunda mitad era cierta, la primera es
irrelevante — /proc/<pid>/cmdline es legible por cualquier proceso local
mientras el verificador corre. Medido: la clave completa aparece ahi. Fix: va
por el ENTORNO del hijo (/proc/<pid>/environ esta restringido al usuario dueno).
No cierra "mismo usuario o root"; saca la clave del alcance de cualquier usuario
local, que es lo que se puede cerrar sin tocar el verificador.

R8-2 — `has_reasoning_trace` se calculaba con la sola existencia del archivo
`<stem>_reasoning_trace.json`, y la UI lo mostraba como badge "trace" y como
"traza: presente". Nunca abria el archivo. `verdict_disagreement` no lo cubre:
compara campos DENTRO de un mismo bundle. Medido: un bundle MALICE con la traza
de OTRO caso (SUSPICION) al lado se mostraba con badge "trace" y
`verdict_disagreement: False` — la afirmacion de R7-1 llevada a la UI, donde
ademas la ve un humano. Fix: un verificador "reasoning_trace" que corre
`verify_tool_log.py <traza> --paired-bundle <bundle>` y reporta su exit code.
"""
from __future__ import annotations

import glob
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CROSS = REPO_ROOT / "vigia" / "results" / "mode1_crosscheck"
MALICE_BUNDLE = CROSS / "FLAREON-2017_mode1_bundle.json"
MALICE_TRACE = CROSS / "FLAREON-2017_mode1_bundle_reasoning_trace.json"
SUSPICION_TRACE = CROSS / "JESS_mode1_bundle_reasoning_trace.json"
CHAIN_BUNDLE = REPO_ROOT / "vigia" / "results" / "ROCBA-CDRIVE_bundle_claude_fable.json"

FAKE_KEY = "ab12cd34" * 8   # 64 hex, ficticia


def _require(*paths):
    for p in paths:
        if not p.exists():
            pytest.skip(f"artefacto de referencia ausente: {p.name}")


@pytest.fixture
def verify_mod():
    from vigia.ui import verify
    return verify


class TestR8HmacKeyNotOnArgv:
    def test_key_is_not_visible_in_proc_cmdline(self, verify_mod):
        """Un proceso local cualquiera leyendo /proc mientras corre la
        verificacion no debe poder leer la clave."""
        _require(CHAIN_BUNDLE)
        found = []

        def snoop():
            deadline = time.time() + 8
            while time.time() < deadline and not found:
                for cmdline in glob.glob("/proc/[0-9]*/cmdline"):
                    try:
                        raw = open(cmdline, "rb").read().replace(b"\x00", b" ").decode(
                            errors="replace")
                    except OSError:
                        continue
                    if FAKE_KEY in raw:
                        found.append(raw)
                        return
                time.sleep(0.001)

        t = threading.Thread(target=snoop)
        t.start()
        verify_mod.run_tool_log(REPO_ROOT, CHAIN_BUNDLE, hmac_key_hex=FAKE_KEY)
        t.join()
        assert not found, f"clave HMAC visible en argv: {found[0][:200]}"

    def test_key_still_reaches_the_verifier(self, verify_mod):
        """Control: el fix no debe romper la verificacion keyed. Este bundle
        se sello SIN clave, asi que con clave provista el verificador exige
        entry_hmac y falla — prueba de que la clave llego."""
        _require(CHAIN_BUNDLE)
        assert verify_mod.run_tool_log(REPO_ROOT, CHAIN_BUNDLE)["status"] == "VERIFIED"
        keyed = verify_mod.run_tool_log(REPO_ROOT, CHAIN_BUNDLE, hmac_key_hex=FAKE_KEY)
        assert keyed["status"] == "BROKEN", keyed.get("detail", "")[-400:]

    def test_key_is_not_echoed_back_to_the_browser(self, verify_mod):
        _require(CHAIN_BUNDLE)
        res = verify_mod.run_tool_log(REPO_ROOT, CHAIN_BUNDLE, hmac_key_hex=FAKE_KEY)
        assert FAKE_KEY not in repr(res)


class TestR8ReasoningTracePairing:
    @pytest.fixture
    def corpus(self):
        _require(MALICE_BUNDLE, MALICE_TRACE, SUSPICION_TRACE)
        tmp = Path(tempfile.mkdtemp())
        shutil.copy(MALICE_BUNDLE, tmp / "ok_mode1_bundle.json")
        shutil.copy(MALICE_TRACE, tmp / "ok_mode1_bundle_reasoning_trace.json")
        shutil.copy(MALICE_BUNDLE, tmp / "swap_mode1_bundle.json")
        shutil.copy(SUSPICION_TRACE, tmp / "swap_mode1_bundle_reasoning_trace.json")
        shutil.copy(MALICE_BUNDLE, tmp / "solo_mode1_bundle.json")
        return tmp

    def test_legitimate_pair_verifies(self, verify_mod, corpus):
        r = verify_mod.run_reasoning_trace(REPO_ROOT, corpus / "ok_mode1_bundle.json")
        assert r["status"] == "VERIFIED", r.get("detail", "")[-600:]

    def test_swapped_trace_is_reported_broken(self, verify_mod, corpus):
        r = verify_mod.run_reasoning_trace(REPO_ROOT, corpus / "swap_mode1_bundle.json")
        assert r["status"] == "BROKEN", r.get("detail", "")[-600:]
        assert "SUSPICION" in r["detail"] and "MALICE" in r["detail"]

    def test_missing_trace_is_absent_not_a_failure(self, verify_mod, corpus):
        r = verify_mod.run_reasoning_trace(REPO_ROOT, corpus / "solo_mode1_bundle.json")
        assert r["status"] == "ABSENT"

    def test_index_flag_alone_proves_nothing(self, corpus):
        """El dato que motiva el fix: la bandera del indice es existencia de
        archivo, y sigue siendo True para el par cruzado. Queda documentado que
        el badge no es una verificacion."""
        from vigia.ui.bundle_index import BundleIndex
        root = corpus.parent / (corpus.name + "_root")
        (root / "results").mkdir(parents=True, exist_ok=True)
        for f in corpus.glob("swap_*"):
            shutil.copy(f, root / "results" / f.name)
        idx = BundleIndex(root, scan_roots=(("results",),))
        idx.refresh(force=True)
        items = idx.query()["items"]
        assert items, "el indice no levanto el bundle"
        entry = items[0]
        assert entry["has_reasoning_trace"] is True
        assert entry["verdict_disagreement"] is False, (
            "verdict_disagreement compara campos dentro del bundle, no "
            "bundle contra traza — si esto cambia, revisar el texto de R8-2")


class TestR8Wiring:
    """Auditoria de la propia rama: `test_endpoint_accepts_the_new_verifier`
    era un grep sobre server.py — habria pasado con el string en un comentario.
    Ahora se ejerce la ruta real y se comprueba que DESPACHA al verificador
    nuevo, y que un nombre inventado sigue siendo rechazado por el modelo."""

    def _client(self, tmp_path):
        pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient
        from vigia.ui.server import create_app
        _require(MALICE_BUNDLE, SUSPICION_TRACE)
        (tmp_path / "results").mkdir()
        shutil.copy(MALICE_BUNDLE, tmp_path / "results" / "x_mode1_bundle.json")
        shutil.copy(SUSPICION_TRACE,
                    tmp_path / "results" / "x_mode1_bundle_reasoning_trace.json")
        for name in ("verify_tool_log.py",):
            shutil.copy(REPO_ROOT / name, tmp_path / name)
        (tmp_path / "forensics").mkdir()
        shutil.copy(REPO_ROOT / "forensics" / "verify_ebs_v1.py",
                    tmp_path / "forensics" / "verify_ebs_v1.py")
        app = create_app(tmp_path)
        return TestClient(app), app

    def _bundle_id(self, app):
        items = app.state.bundle_index.query()["items"]
        assert items, "el indice no levanto el bundle de prueba"
        return items[0]["id"]

    def test_endpoint_dispatches_to_the_new_verifier(self, tmp_path):
        client, app = self._client(tmp_path)
        bid = self._bundle_id(app)
        r = client.post(f"/api/bundles/{bid}/verify",
                        json={"verifier": "reasoning_trace"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["verifier"] == "reasoning_trace"
        # el par es cruzado a proposito: la traza es de otro caso
        assert body["status"] == "BROKEN", body
        assert "SUSPICION" in body["detail"] and "MALICE" in body["detail"]

    def test_unknown_verifier_is_still_rejected(self, tmp_path):
        client, app = self._client(tmp_path)
        bid = self._bundle_id(app)
        r = client.post(f"/api/bundles/{bid}/verify",
                        json={"verifier": "inventado"})
        assert r.status_code == 422, r.text

    def test_frontend_offers_it_and_has_both_locales(self):
        app_js = (REPO_ROOT / "vigia" / "ui" / "static" / "app.js").read_text()
        assert '"reasoning_trace"' in app_js
        i18n = (REPO_ROOT / "vigia" / "ui" / "static" / "i18n.js").read_text()
        assert i18n.count('"verify.name.reasoning_trace"') == 2, "falta EN o ES"
