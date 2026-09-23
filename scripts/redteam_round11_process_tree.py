"""
Red Team Round 11 — terminacion del arbol de procesos del JobRunner.

Levanta el JobRunner REAL con un `vigia_agent.py` de mentira que lanza una
herramienta de larga duracion (el rol que cumplen volatility, tshark y
regripper via sift_orchestrator), y mide si esa herramienta sobrevive a un
timeout de job y a un shutdown del servidor.

Uso:
    python3 scripts/redteam_round11_process_tree.py
    # contra el jobs.py pre-R11 -> "sigue corriendo: True" en ambos escenarios

Exit 0 si ninguna sobrevive; 1 si alguna lo hace.
"""
import os, shutil, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/home/user/vigia-intent-analysis")
from vigia.ui.jobs import JobRunner

def corriendo(pid):
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().rsplit(") ", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return False

def montar(tmp, pidf):
    """Un 'agente' que lanza una herramienta SIFT de larga duracion."""
    (tmp / "cases" / "caso").mkdir(parents=True)
    (tmp / "cases" / "caso" / "ev.txt").write_text("evidencia")
    (tmp / "vigia_agent.py").write_text(
        "import subprocess, sys, time\n"
        "subprocess.Popen([sys.executable, '-c',\n"
        "  \"import time, os\\nopen(%r,'w').write(str(os.getpid()))\\ntime.sleep(300)\"])\n"
        "print('herramienta lanzada', flush=True)\n"
        "time.sleep(300)\n" % str(pidf))

def escenario(nombre, accion, timeout_s=3):
    tmp = Path(tempfile.mkdtemp()); pidf = tmp / "tool.pid"
    montar(tmp, pidf)
    r = JobRunner(tmp, agent_script=tmp / "vigia_agent.py", timeout_s=timeout_s)
    r.submit(evidence_path="cases/caso", case_id="CASO-R11")
    for _ in range(60):
        if pidf.exists(): break
        time.sleep(0.2)
    tool = int(pidf.read_text())
    accion(r)
    time.sleep(4)
    vivo = corriendo(tool)
    print(f"  {nombre:40} herramienta SIFT sigue corriendo: {vivo}")
    if vivo:
        try: os.killpg(os.getpgid(tool), 9)
        except OSError: pass
    shutil.rmtree(tmp, ignore_errors=True)
    return vivo

print("El 'agente' lanza una herramienta que tarda 300s. Timeout de job = 3s.\n")
a = escenario("timeout del job", lambda r: time.sleep(5))
b = escenario("shutdown del servidor", lambda r: r.shutdown(), timeout_s=600)
sys.exit(1 if (a or b) else 0)

