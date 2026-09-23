"""
Test R9-1 — la UI no puede irse de loopback en silencio.

`VIGIA_HOST` lo leen DOS servicios: la API Modo 5 (`vigia/vigia_api.py`, puerto
8000) y esta web UI (puerto 8010). INSTALL.md le dice al operador que necesita
acceso remoto a la API que la ponga detras de un proxy inverso autenticado; si
para eso setea `VIGIA_HOST=0.0.0.0`, la UI se iba con ella — sin auth de ningun
tipo y con `POST /api/investigations`, que lanza `vigia_agent.py` como
subproceso.

Medido antes del fix, con el servidor real:

    INFO: Uvicorn running on http://0.0.0.0:8099
    POST /api/investigations  (sin Origin, sin Referer)  -> HTTP 422
    GET  /api/evidence        (sin credencial)           -> inventario completo

El 422 es validacion de negocio ("evidence path does not exist"): la peticion
atraveso el guard cross-site y llego al lanzador. No hay puerta de autenticacion
en ningun punto del camino.

Alcance honesto de la medicion: se confirmo el bind a 0.0.0.0 y la ausencia de
auth desde loopback dentro del sandbox. NO se demostro un atacante remoto en una
LAN — eso no es reproducible aca, y el bind mas la ausencia de auth alcanzan
para establecer la exposicion sin afirmar de mas.

Fix: la UI lee su propia `VIGIA_UI_HOST` primero, y se NIEGA a arrancar en una
direccion no-loopback salvo que `VIGIA_UI_ALLOW_REMOTE` diga que el operador lo
quiso. Negarse es la opcion honest-degradation: una exposicion que nadie pidio
es peor que un servidor que no levanta y explica por que.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))



def _entry():
    """Import diferido: los tests de comportamiento (subprocess, launcher)
    deben poder correr contra un checkout que todavia no tiene estas
    funciones, o el control negativo solo probaria que el import falla."""
    import importlib
    return importlib.import_module("vigia.ui.__main__")


def is_loopback(host):
    return _entry().is_loopback(host)


def resolve_host():
    return _entry().resolve_host()


def remote_bind_refusal(host, source):
    return _entry().remote_bind_refusal(host, source)


class TestIsLoopback:
    @pytest.mark.parametrize("host", [
        "127.0.0.1", "127.0.0.53", "::1", "[::1]", "localhost", "LOCALHOST",
        "localhost.localdomain", " 127.0.0.1 ",
    ])
    def test_loopback_accepted(self, host):
        assert is_loopback(host)

    @pytest.mark.parametrize("host", [
        "0.0.0.0", "::", "192.168.1.10", "10.0.0.1", "example.com",
        "127.0.0.1.evil.com", "",
    ])
    def test_non_loopback_rejected(self, host):
        assert not is_loopback(host)

    def test_unresolvable_name_is_not_assumed_safe(self):
        """Un nombre que no podemos evaluar lexicamente no se da por local."""
        assert not is_loopback("mi-workstation")


class TestResolveHost:
    def _clean(self, monkeypatch):
        for var in ("VIGIA_UI_HOST", "VIGIA_HOST", "VIGIA_UI_ALLOW_REMOTE"):
            monkeypatch.delenv(var, raising=False)

    def test_default_is_loopback(self, monkeypatch):
        self._clean(monkeypatch)
        host, source = resolve_host()
        assert is_loopback(host) and source == "default"

    def test_shared_variable_is_still_honoured(self, monkeypatch):
        self._clean(monkeypatch)
        monkeypatch.setenv("VIGIA_HOST", "0.0.0.0")
        assert resolve_host() == ("0.0.0.0", "VIGIA_HOST")

    def test_ui_variable_wins_over_the_shared_one(self, monkeypatch):
        """El desacople: exponer la API sin arrastrar la UI."""
        self._clean(monkeypatch)
        monkeypatch.setenv("VIGIA_HOST", "0.0.0.0")
        monkeypatch.setenv("VIGIA_UI_HOST", "127.0.0.1")
        assert resolve_host() == ("127.0.0.1", "VIGIA_UI_HOST")

    def test_blank_value_falls_through(self, monkeypatch):
        self._clean(monkeypatch)
        monkeypatch.setenv("VIGIA_UI_HOST", "   ")
        monkeypatch.setenv("VIGIA_HOST", "127.0.0.1")
        assert resolve_host() == ("127.0.0.1", "VIGIA_HOST")


class TestRefusalMessage:
    def test_names_the_shared_variable_when_that_is_the_source(self):
        msg = remote_bind_refusal("0.0.0.0", "VIGIA_HOST")
        assert "Mode 5 API" in msg
        assert "VIGIA_UI_HOST" in msg and "VIGIA_UI_ALLOW_REMOTE" in msg
        assert "no authentication" in msg

    def test_omits_the_shared_note_when_ui_variable_was_explicit(self):
        msg = remote_bind_refusal("0.0.0.0", "VIGIA_UI_HOST")
        assert "Mode 5 API" not in msg
        assert "VIGIA_UI_ALLOW_REMOTE" in msg


class TestEntryPointRefuses:
    """El comportamiento observable: el proceso no levanta."""

    def _run(self, env_extra, timeout=45):
        env = dict(os.environ)
        for var in ("VIGIA_UI_HOST", "VIGIA_HOST", "VIGIA_UI_ALLOW_REMOTE"):
            env.pop(var, None)
        env.update(env_extra)
        env["VIGIA_UI_PORT"] = "8094"
        return subprocess.run([sys.executable, "-m", "vigia.ui"],
                              capture_output=True, text=True,
                              cwd=str(REPO_ROOT), env=env, timeout=timeout)

    def test_shared_variable_pointing_off_loopback_is_refused(self):
        pytest.importorskip("uvicorn")
        r = self._run({"VIGIA_HOST": "0.0.0.0"})
        assert r.returncode != 0
        out = r.stdout + r.stderr
        assert "REFUSING to bind" in out, out[-500:]
        assert "Uvicorn running" not in out

    def test_ui_variable_pointing_off_loopback_is_refused(self):
        pytest.importorskip("uvicorn")
        r = self._run({"VIGIA_UI_HOST": "0.0.0.0"})
        assert r.returncode != 0
        assert "REFUSING to bind" in (r.stdout + r.stderr)


class TestLauncherScript:
    def test_shell_launcher_prefers_the_ui_variable(self):
        src = (REPO_ROOT / "launch_vigia_ui.sh").read_text()
        assert 'HOST="${VIGIA_UI_HOST:-${VIGIA_HOST:-127.0.0.1}}"' in src, (
            "el echo del launcher imprimiria una URL distinta de la real")
