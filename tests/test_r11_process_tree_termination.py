"""
Test R11-1 — el JobRunner terminaba un pid, no un arbol.

`jobs.py` lanza el agente con `start_new_session=True`, que lo hace lider de su
propia sesion y grupo de procesos. Eso existe precisamente para poder señalar al
arbol entero sin tocar al servidor. Pero `_kill` (timeout) y `shutdown`
llamaban `proc.terminate()`, que señala UN pid — el mecanismo estaba puesto y
sin usar, la misma firma que `prev_hash` en R10-1 y que `_signal_z_fraction` en
R10-4.

Alcance, verificado por cadena de imports y no supuesto: `vigia_agent.py` llega
via `sift_orchestrator` a `memory_forensics`, `pcap_parser` y
`registry_timeline_reconstructor`, que corren volatility3, tshark y regripper
como subprocesos, con timeouts propios de hasta 120s y, para volatility, un
`vol3_effective_timeout` calculado. Sobre una imagen de memoria eso son minutos
u horas.

Medido con el JobRunner real y un agente de prueba que lanza una herramienta de
300s:

    codigo pre-R11:   timeout del job      -> herramienta sigue corriendo: True
                      shutdown del servidor -> herramienta sigue corriendo: True
    post-fix:         ambos                 -> False

Consecuencia: la UI decia "process terminated" mientras la herramienta pesada
seguia viva sobre la evidencia, y el slot de concurrencia (max 1 por defecto)
quedaba libre para un job nuevo que arrancaba junto al fantasma.

NOTA SOBRE EL ORACULO — la primera medicion de esta ronda dio un falso
"tambien sobrevive a killpg". La causa era el oraculo, no el codigo:
`os.kill(pid, 0)` tiene EXITO sobre un zombie, asi que un proceso ya muerto y
no cosechado se contaba como vivo. El oraculo correcto lee el estado en
`/proc/<pid>/stat` y descarta 'Z'. Se deja escrito porque un oraculo que no
distingue zombie de vivo invalida cualquier medicion de terminacion.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from vigia.ui.jobs import JobRunner  # noqa: E402


def _signal_process_tree(proc, sig):
    """Import diferido — mismo motivo que en R9: con el import a nivel de
    modulo, contra un checkout que todavia no tiene la funcion la COLECCION
    falla con ImportError y los tests de comportamiento nunca llegan a correr.
    Eso probaria que la funcion no existe, no que los tests atrapen la
    conducta vieja. (Error cometido en R9, corregido alli, y repetido aca en
    el primer intento.)"""
    import importlib
    return importlib.import_module("vigia.ui.jobs")._signal_process_tree(proc, sig)

pytestmark = pytest.mark.skipif(
    not Path("/proc").is_dir(), reason="el oraculo de estado necesita /proc")


def _running(pid: int) -> bool:
    """Vivo Y no zombie — ver la nota sobre el oraculo en el docstring."""
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(") ", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False


def _fake_agent(tmp: Path, pidfile: Path) -> None:
    (tmp / "cases" / "caso").mkdir(parents=True)
    (tmp / "cases" / "caso" / "ev.txt").write_text("evidencia")
    (tmp / "vigia_agent.py").write_text(
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-c',\n"
        "  \"import time, os\\nopen(%r,'w').write(str(os.getpid()))\\ntime.sleep(300)\"])\n"
        "print('herramienta lanzada', flush=True)\n"
        "time.sleep(300)\n" % str(pidfile))


def _fake_agent_that_exits_before_its_child(tmp: Path, pidfile: Path) -> None:
    (tmp / "cases" / "caso").mkdir(parents=True)
    (tmp / "cases" / "caso" / "ev.txt").write_text("evidencia")
    (tmp / "vigia_agent.py").write_text(
        "import subprocess, sys\n"
        "subprocess.Popen([sys.executable, '-c',\n"
        "  \"import time, os\\nopen(%r,'w').write(str(os.getpid()))\\ntime.sleep(300)\"])\n"
        "print('agent exits', flush=True)\n" % str(pidfile))


@pytest.fixture
def runner_con_herramienta():
    creados = []

    def _make(timeout_s: int):
        tmp = Path(tempfile.mkdtemp())
        creados.append(tmp)
        pidfile = tmp / "tool.pid"
        _fake_agent(tmp, pidfile)
        runner = JobRunner(tmp, agent_script=tmp / "vigia_agent.py",
                           timeout_s=timeout_s)
        runner.submit(evidence_path="cases/caso", case_id="CASO-R11")
        for _ in range(100):
            if pidfile.exists():
                break
            time.sleep(0.2)
        assert pidfile.exists(), "el agente de prueba no lanzo la herramienta"
        return runner, int(pidfile.read_text())

    yield _make
    for tmp in creados:
        shutil.rmtree(tmp, ignore_errors=True)


class TestTimeoutReachesTheWholeTree:
    def test_sift_tool_does_not_survive_a_job_timeout(self, runner_con_herramienta):
        runner, tool = runner_con_herramienta(3)
        time.sleep(9)
        assert not _running(tool), (
            "la herramienta sobrevivio al timeout: la UI dice 'terminated' "
            "mientras el proceso sigue sobre la evidencia")

    def test_job_is_marked_as_timed_out(self, runner_con_herramienta):
        runner, tool = runner_con_herramienta(3)
        time.sleep(9)
        snap = runner.list_jobs()[0]
        assert snap["state"] == "error"
        assert "timeout" in (snap["error"] or "")


class TestTimeoutDoesNotBrickTheLauncher:
    """R11-2 — consecuencia que la medicion destapo y la lectura no habia
    previsto: el huerfano hereda el pipe de stdout del agente, asi que el
    bucle `for line in proc.stdout` NUNCA ve EOF. `proc.wait()` no corre, el
    job se queda en 'running' para siempre y el `finally: self._slots.release()`
    no se ejecuta jamas. Con `max_jobs=1` por defecto, UN solo timeout dejaba
    el lanzador Modo 1 inutilizable hasta reiniciar el servidor.

    Medido: pre-fix, estado 'running' y segundo submit rechazado con 409;
    post-fix, estado 'error' y segundo submit aceptado.
    """

    def test_job_reaches_a_terminal_state(self, runner_con_herramienta):
        runner, _tool = runner_con_herramienta(3)
        time.sleep(9)
        snap = runner.list_jobs()[0]
        assert snap["state"] in ("error", "done"), (
            f"el job quedo en {snap['state']!r}: el bucle de lectura sigue "
            f"bloqueado sobre un pipe que el huerfano mantiene abierto")

    def test_slot_is_released_so_a_second_job_can_run(self, runner_con_herramienta):
        from vigia.ui.jobs import JobBusyError
        runner, _tool = runner_con_herramienta(3)
        time.sleep(9)
        try:
            runner.submit(evidence_path="cases/caso", case_id="SEGUNDO-R11")
        except JobBusyError as exc:
            pytest.fail(f"el slot no se libero tras el timeout: {exc}")
        runner.shutdown()

    def test_exited_leader_does_not_hide_a_live_child(self, monkeypatch):
        """The group ID survives its leader: timeout must still kill it."""
        import vigia.ui.jobs as jobs
        monkeypatch.setattr(jobs, "_TERMINATE_GRACE_S", 0)
        tmp = Path(tempfile.mkdtemp())
        try:
            pidfile = tmp / "tool.pid"
            _fake_agent_that_exits_before_its_child(tmp, pidfile)
            runner = JobRunner(tmp, agent_script=tmp / "vigia_agent.py", timeout_s=1)
            runner.submit(evidence_path="cases/caso", case_id="EXITED-LEADER")
            for _ in range(100):
                if pidfile.exists():
                    break
                time.sleep(0.05)
            assert pidfile.exists()
            tool = int(pidfile.read_text())
            time.sleep(2)
            assert not _running(tool), "child survived after its leader exited"
            assert runner.list_jobs()[0]["state"] == "error"
        finally:
            runner.shutdown() if "runner" in locals() else None
            shutil.rmtree(tmp, ignore_errors=True)


class TestShutdownReachesTheWholeTree:
    def test_sift_tool_does_not_survive_server_shutdown(self, runner_con_herramienta):
        runner, tool = runner_con_herramienta(600)
        runner.shutdown()
        time.sleep(5)
        assert not _running(tool), (
            "la herramienta sobrevivio al shutdown: el servidor se fue y "
            "nadie la mira")


class TestSignalHelper:
    def test_targets_the_group_when_the_child_leads_its_own(self):
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                start_new_session=True)
        try:
            alcance = _signal_process_tree(proc, 15)  # SIGTERM
            assert "grupo de procesos" in alcance, alcance
            proc.wait(timeout=10)
        finally:
            if proc.poll() is None:
                proc.kill()

    def test_never_signals_the_servers_own_group(self):
        """Sin start_new_session el hijo comparte grupo con el servidor:
        señalar el grupo se llevaria puesto al propio proceso. El helper debe
        caer a señalar el pid."""
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            assert os.getpgid(proc.pid) == os.getpgid(0), "premisa del test"
            alcance = _signal_process_tree(proc, 15)
            assert alcance == f"sólo el pid {proc.pid}", alcance
            proc.wait(timeout=10)
        finally:
            if proc.poll() is None:
                proc.kill()

    def test_dead_process_is_reported_not_raised(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait(timeout=10)
        alcance = _signal_process_tree(proc, 15)
        assert isinstance(alcance, str) and alcance


class TestOracleSanity:
    """El oraculo que invalido la primera medicion, fijado como control."""

    def test_zombie_is_not_counted_as_running(self):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        time.sleep(1)                      # muerto, sin cosechar -> zombie
        try:
            with open(f"/proc/{proc.pid}/stat") as fh:
                estado = fh.read().rsplit(") ", 1)[1].split()[0]
        except (OSError, IndexError):
            pytest.skip("el proceso ya fue cosechado por el entorno")
        if estado != "Z":
            pytest.skip("no se pudo producir un zombie de forma fiable aca")
        assert not _running(proc.pid)
        os.kill(proc.pid, 0)               # os.kill(...,0) SI tiene exito: por eso fallaba
        proc.wait()
