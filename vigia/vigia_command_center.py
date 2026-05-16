#!/usr/bin/env python3
"""
vigia_command_center.py
─────────────────────────────────────────────────────────────────────────────
VIGÍA Forensic Suite — Command Center (TUI)

Tablero de mando en terminal que consume archivos .jsonl en tiempo real.
Muestra:
  • Últimos hypothesis_id ganadores con cobertura y costo
  • Gráfico de barras de entropía de red (historial)
  • Estado de GPU (carga, VRAM, temperatura)
  • Últimas anomalías detectadas con severidad
  • Métricas de la cadena de custodia (integridad)
  • Contador de decisiones ACCEPT/REJECT/ABSTAIN

Dependencias:
  rich>=13.0      — siempre disponible
  entropy_kernel  — VIGÍA kernel de entropía (mismo repo); provee entropy_normalized()
  textual         — opcional, activa layout avanzado si está instalado
  pynvml          — opcional, monitoreo de GPU (NVIDIA)

Uso:
  python3 vigia_command_center.py --watch ./red_team/
  python3 vigia_command_center.py --watch . --refresh 2
  python3 vigia_command_center.py --demo      # genera datos sintéticos para demostración

─────────────────────────────────────────────────────────────────────────────
VIGÍA SANS FIND EVIL Hackathon 2026
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

# VIGÍA internal — mismo repo, debe estar en PYTHONPATH o directorio raíz
from entropy_kernel import entropy_normalized  # Fix2-2026-05-16: reemplaza _shannon_entropy_fast

# Fix4-2026-05-16: límite para deduplicación de eventos — evita memory creep
# ~10MB de strings; suficiente para semanas de procesamiento continuo
_MAX_SEEN_IDS: int = 50_000

# ══════════════════════════════════════════════════════════════════════════
# GPU MONITOR (opcional — pynvml para GPUs NVIDIA)
# ══════════════════════════════════════════════════════════════════════════

_NVML_AVAILABLE = False
_nvml_handle = None

def _init_nvml() -> bool:
    global _NVML_AVAILABLE, _nvml_handle
    try:
        import pynvml
        pynvml.nvmlInit()
        _nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        _NVML_AVAILABLE = True
        return True
    except Exception:
        return False


def _get_gpu_stats() -> Dict:
    if not _NVML_AVAILABLE or _nvml_handle is None:
        return {"available": False}
    try:
        import pynvml
        util = pynvml.nvmlDeviceGetUtilizationRates(_nvml_handle)
        mem = pynvml.nvmlDeviceGetMemoryInfo(_nvml_handle)
        temp = pynvml.nvmlDeviceGetTemperature(_nvml_handle, pynvml.NVML_TEMPERATURE_GPU)
        name = pynvml.nvmlDeviceGetName(_nvml_handle)
        if isinstance(name, bytes):
            name = name.decode()
        return {
            "available": True,
            "name":       name,
            "gpu_util":   util.gpu,
            "mem_used_gb": round(mem.used / 1e9, 2),
            "mem_total_gb": round(mem.total / 1e9, 2),
            "mem_pct":    round(mem.used / mem.total * 100, 1),
            "temp_c":     temp,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ══════════════════════════════════════════════════════════════════════════
# STATE — buffer circular de eventos
# ══════════════════════════════════════════════════════════════════════════

class VigiAState:
    MAX_HYPOTHESES = 12
    MAX_ANOMALIES  = 8
    MAX_ENTROPY    = 30   # historial de puntos de entropía

    def __init__(self) -> None:
        self.hypotheses:  Deque[Dict] = deque(maxlen=self.MAX_HYPOTHESES)
        self.anomalies:   Deque[Dict] = deque(maxlen=self.MAX_ANOMALIES)
        self.entropy_history: Deque[float] = deque(maxlen=self.MAX_ENTROPY)
        self.decisions:   Dict[str, int] = {"ACCEPT": 0, "REJECT": 0, "ABSTAIN": 0}
        self.chain_status: Dict = {}
        self.last_update:  str = "—"
        self.files_processed: int = 0
        self.total_cases:  int = 0
        self.engine_mode:  str = "LIVE"
        # Fix3-2026-05-16: offsets por archivo — lectura incremental O(n) en vez de O(n²)
        self._file_offsets: Dict[str, int] = {}
        # Fix4-2026-05-16: bounded deduplicación — evita memory creep en sesiones largas
        # ~10MB para 50k strings de case_id; evicción FIFO cuando se llena
        self._seen_ids:    set = set()
        self._seen_queue:  deque = deque()  # Fix4b: sin maxlen, control manual explícito

    def ingest_jsonl(self, path: str, offset: int = 0) -> Tuple[int, int]:
        """
        Lee un archivo .jsonl desde `offset` bytes e ingiere los eventos nuevos.

        Fix3-2026-05-16: lectura incremental — evita releer todo el archivo en
        cada refresh (O(n²) → O(n) amortizado en archivos crecientes).

        Returns:
            Tuple[int, int]: (nuevos_eventos, nuevo_offset)
        """
        new = 0
        new_offset = offset
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                f.seek(offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        self._process_event(event, path)
                        new += 1
                    except json.JSONDecodeError:
                        continue
                new_offset = f.tell()
        except Exception:
            pass
        return new, new_offset

    def _process_event(self, event: Dict, source: str) -> None:
        case_id = event.get("case_id", "")
        if case_id in self._seen_ids:
            return
        if case_id:
            # Fix4b-2026-05-16: evicción FIFO explícita. Invariante exacta:
            # _seen_ids == set(_seen_queue) siempre. No depende de side-effects
            # internos de CPython deque(maxlen). ChatGPT audit post-fix.
            if len(self._seen_queue) >= _MAX_SEEN_IDS:
                oldest = self._seen_queue.popleft()  # determinista, visible
                self._seen_ids.discard(oldest)
            self._seen_queue.append(case_id)
            self._seen_ids.add(case_id)

        self.total_cases += 1
        self.last_update = _utcnow_short()

        # Extraer hypothesis ganadora
        hyp_id = event.get("expected_hypothesis", "")
        vector = event.get("adversarial_vector", "")
        verdict = event.get("expected_verdict", "")
        inc_cov = event.get("incomplete_coverage_expected", False)

        if hyp_id:
            self.hypotheses.append({
                "id":       hyp_id,
                "verdict":  verdict,
                "vector":   vector,
                "inc_cov":  inc_cov,
                "source":   Path(source).name,
                "ts":       _utcnow_short(),
            })

        # Decisiones
        d = verdict.upper()
        if d in self.decisions:
            self.decisions[d] += 1

        # Entropía desde artefactos — usa entropy_kernel.entropy_normalized (Fix2-2026-05-16)
        # Semántica: 0.0 = concentrado (bot), 1.0 = uniforme (humano). Ver entropy_kernel.py.
        for art in event.get("artifacts", []):
            intervals = art.get("intervals_ms", [])
            if intervals and len(intervals) >= 4:
                e = entropy_normalized(intervals)
                self.entropy_history.append(round(e, 3))
                break

        # Anomalías
        note = event.get("adversarial_note", "")
        if note:
            self.anomalies.append({
                "case_id": case_id or "?",
                "vector":  vector,
                "note":    note[:80],
                "ts":      _utcnow_short(),
            })


def _utcnow_short() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


# ══════════════════════════════════════════════════════════════════════════
# RENDER — constructores de paneles Rich
# ══════════════════════════════════════════════════════════════════════════

def _color_verdict(v: str) -> str:
    return {
        "MALICE":    "bold red",
        "SUSPICION": "yellow",
        "NOISE":     "green",
        "ABSTAIN":   "dim",
        "REJECT":    "bold red",
        "ACCEPT":    "bold green",
    }.get(v.upper(), "white")


def _color_vector(v: str) -> str:
    return {
        "V1_MISSING_CRITICAL_ARTIFACT": "red",
        "V2_COVERAGE_DECOY":            "yellow",
        "V3_COST_COLLISION":            "cyan",
        "V4_PHASE_POLYMORPHISM":        "magenta",
        "COMPOUND_APT_XF":              "bold red",
    }.get(v, "white")


def render_header() -> Panel:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = Text()
    title.append("▓▓▓ ", style="bold red")
    title.append("VIGÍA", style="bold white on red")
    title.append(" COMMAND CENTER", style="bold white")
    title.append("  ▓▓▓", style="bold red")
    title.append(f"  {now}", style="dim")
    return Panel(Align.center(title), style="bold red", padding=(0, 2))


def render_gpu_panel(gpu: Dict) -> Panel:
    if not gpu.get("available"):
        content = Text("GPU no disponible\n(pynvml no instalado)", style="dim", justify="center")
        return Panel(content, title="[bold]GPU[/bold]", style="dim", height=8)

    name = gpu.get("name", "GPU")
    util = gpu.get("gpu_util", 0)
    mem_used = gpu.get("mem_used_gb", 0)
    mem_total = gpu.get("mem_total_gb", 24)
    mem_pct = gpu.get("mem_pct", 0)
    temp = gpu.get("temp_c", 0)

    # Color temperatura
    if temp > 80:
        temp_style = "bold red"
    elif temp > 70:
        temp_style = "yellow"
    else:
        temp_style = "green"

    # Barra de utilización GPU
    util_bar = _mini_bar(util, 100, width=20)
    mem_bar  = _mini_bar(int(mem_pct), 100, width=20)

    t = Table.grid(padding=(0, 1))
    t.add_column(style="dim", width=12)
    t.add_column(width=28)
    t.add_row("Modelo:", Text(name, style="bold white"))
    t.add_row("GPU:", Text(f"{util_bar} {util}%",
                           style="bold green" if util > 80 else "green"))
    t.add_row("VRAM:", Text(f"{mem_bar} {mem_used}/{mem_total}GB",
                            style="yellow" if mem_pct > 70 else "white"))
    t.add_row("Temp:", Text(f"{temp}°C", style=temp_style))

    return Panel(t, title=f"[bold cyan]{name}[/bold cyan]",
                 style="cyan", border_style="cyan")


def _mini_bar(value: int, total: int, width: int = 20) -> str:
    filled = round(value / max(total, 1) * width)
    if value > 80:
        char = "█"
    elif value > 50:
        char = "▓"
    else:
        char = "░"
    return char * filled + "░" * (width - filled)


def render_hypotheses_table(state: VigiAState) -> Panel:
    t = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE_HEAVY,
        expand=True,
        show_edge=False,
    )
    t.add_column("Hypothesis ID", style="bold", width=12)
    t.add_column("Veredicto", width=11)
    t.add_column("Vector", width=28)
    t.add_column("Inc.Cov", width=7)
    t.add_column("Hora", width=8)

    entries = list(state.hypotheses)[::-1]  # más reciente primero
    for h in entries[:10]:
        ic_text = Text("⚠ SÍ", style="yellow") if h["inc_cov"] else Text("OK", style="green")
        t.add_row(
            Text(h["id"], style="bold white"),
            Text(h["verdict"], style=_color_verdict(h["verdict"])),
            Text(h["vector"][:28], style=_color_vector(h["vector"])),
            ic_text,
            Text(h["ts"], style="dim"),
        )

    if not entries:
        t.add_row("[dim]Sin datos[/dim]", "", "", "", "")

    return Panel(t, title=f"[bold]Últimas Hipótesis Ganadoras[/bold] ({len(state.hypotheses)})",
                 style="white", border_style="white")


def render_entropy_chart(state: VigiAState) -> Panel:
    history = list(state.entropy_history)

    if not history:
        content = Text("Sin datos de entropía", style="dim", justify="center")
        return Panel(content, title="[bold yellow]Entropía de Red[/bold yellow]",
                     style="yellow", height=10)

    # Normalizar a [0, max_val] para barras
    max_val = max(history) if history else 1.0
    min_val = min(history) if history else 0.0
    range_val = max_val - min_val or 1.0

    # Gráfico ASCII de barras horizontales
    BAR_WIDTH = 35
    lines = []

    # Escala: los últimos MAX_ENTROPY puntos
    for i, val in enumerate(history[-15:]):
        norm = (val - min_val) / range_val
        filled = round(norm * BAR_WIDTH)

        if val > 4.0:
            color = "green"  # alta entropía = tráfico humano/legítimo
        elif val > 2.0:
            color = "yellow"
        else:
            color = "red"   # entropía baja = posible beacon/script

        bar = "█" * filled + "░" * (BAR_WIDTH - filled)
        lines.append(
            Text(f"  {val:6.3f} ") +
            Text(f"[{bar}]", style=color)
        )

    # Estadísticas
    avg = sum(history) / len(history)
    last = history[-1]
    trend = "↑" if len(history) >= 2 and history[-1] > history[-2] else "↓"

    stats = Text(f"\n  Último: {last:.3f} {trend}  |  Promedio: {avg:.3f}  |  "
                 f"Rango: [{min_val:.2f}, {max_val:.2f}]", style="dim")

    # Leyenda
    legend = Text("\n  [rojo < 2.0 = beacon posible]  "
                  "[amarillo = ambiguo]  [verde > 4.0 = orgánico]", style="dim")

    content = Text()
    for line in lines:
        content.append_text(line)
        content.append("\n")
    content.append_text(stats)
    content.append_text(legend)

    return Panel(content, title="[bold yellow]Entropía de Red (últimos puntos)[/bold yellow]",
                 style="yellow", border_style="yellow")


def render_decisions_panel(state: VigiAState) -> Panel:
    total = sum(state.decisions.values()) or 1

    t = Table.grid(padding=(0, 2))
    t.add_column(width=10)
    t.add_column(width=6)
    t.add_column(width=20)

    for decision, count in state.decisions.items():
        pct = round(count / total * 100)
        bar = _mini_bar(pct, 100, width=15)
        style = _color_verdict(decision)
        t.add_row(
            Text(decision, style=style + " bold"),
            Text(str(count), style=style),
            Text(f"[{bar}] {pct}%", style=style),
        )

    return Panel(t, title="[bold]Decisiones[/bold]",
                 border_style="white", style="white")


def render_anomalies_panel(state: VigiAState) -> Panel:
    t = Table(
        show_header=False,
        box=None,
        expand=True,
        padding=(0, 1),
    )
    t.add_column("ID", width=14)
    t.add_column("Nota", style="dim")

    for a in list(state.anomalies)[::-1][:6]:
        vec_style = _color_vector(a["vector"])
        t.add_row(
            Text(a["case_id"][:14], style=vec_style),
            Text(a["note"][:55], style="dim"),
        )

    if not state.anomalies:
        t.add_row("[dim]Sin anomalías[/dim]", "")

    return Panel(t, title="[bold red]Anomalías Recientes[/bold red]",
                 border_style="red", style="red")


def render_stats_footer(state: VigiAState) -> Panel:
    text = Text()
    text.append(f" Casos procesados: ", style="dim")
    text.append(str(state.total_cases), style="bold white")
    text.append("  |  Archivos: ", style="dim")
    text.append(str(state.files_processed), style="bold white")
    text.append("  |  Último update: ", style="dim")
    text.append(state.last_update, style="bold white")
    text.append("  |  Motor: ", style="dim")
    text.append(state.engine_mode, style="bold cyan")
    text.append("  |  [dim]q/Ctrl+C para salir[/dim]")
    return Panel(text, style="dim", padding=(0, 1))


def build_layout(state: VigiAState, gpu: Dict) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header",  size=3),
        Layout(name="body",    ratio=1),
        Layout(name="footer",  size=3),
    )
    layout["body"].split_row(
        Layout(name="left",  ratio=2),
        Layout(name="right", ratio=1),
    )
    layout["left"].split_column(
        Layout(name="hypotheses", ratio=2),
        Layout(name="entropy",    ratio=1),
    )
    layout["right"].split_column(
        Layout(name="gpu",       size=8),
        Layout(name="decisions", size=8),
        Layout(name="anomalies", ratio=1),
    )

    layout["header"].update(render_header())
    layout["hypotheses"].update(render_hypotheses_table(state))
    layout["entropy"].update(render_entropy_chart(state))
    layout["gpu"].update(render_gpu_panel(gpu))
    layout["decisions"].update(render_decisions_panel(state))
    layout["anomalies"].update(render_anomalies_panel(state))
    layout["footer"].update(render_stats_footer(state))

    return layout


# ══════════════════════════════════════════════════════════════════════════
# DEMO DATA GENERATOR
# ══════════════════════════════════════════════════════════════════════════

def generate_demo_events(rng: random.Random, n: int = 5) -> List[Dict]:
    vectors = ["V1_MISSING_CRITICAL_ARTIFACT", "V2_COVERAGE_DECOY",
               "V3_COST_COLLISION", "V4_PHASE_POLYMORPHISM", "COMPOUND_APT_XF"]
    hyps = ["H_DE_001", "H_XF_001", "H_PE_001", "H_LM_001", "H_IA_001", "H_EX_001"]
    verdicts = ["MALICE", "SUSPICION", "NOISE", "ABSTAIN"]

    events = []
    for i in range(n):
        intervals = [2000 + rng.randint(-50, 200) for _ in range(30)]
        events.append({
            "case_id":                    f"DEMO_{rng.randint(1000, 9999)}",
            "expected_hypothesis":        rng.choice(hyps),
            "expected_verdict":           rng.choice(verdicts),
            "adversarial_vector":         rng.choice(vectors),
            "incomplete_coverage_expected": rng.random() < 0.3,
            "adversarial_note":           f"Evento demo #{i} — vector activo",
            "artifacts": [{
                "artifact_name":  "log_gap_intervals",
                "intervals_ms":   intervals,
            }],
        })
    return events


# ══════════════════════════════════════════════════════════════════════════
# WATCHER — polling de archivos .jsonl
# ══════════════════════════════════════════════════════════════════════════

def run_dashboard(
    watch_paths: List[str],
    refresh: float = 2.0,
    demo_mode: bool = False,
) -> None:
    console = Console()
    state = VigiAState()
    gpu = {"available": False}

    _init_nvml()

    # Fix3-2026-05-16: offsets viven en state._file_offsets; processed_files eliminado
    def scan_and_ingest() -> None:
        for pattern in watch_paths:
            for fpath in glob.glob(pattern, recursive=True):
                last_offset = state._file_offsets.get(fpath, 0)
                new, new_offset = state.ingest_jsonl(fpath, last_offset)
                if new > 0:
                    state._file_offsets[fpath] = new_offset
                    state.files_processed = len(state._file_offsets)

    # Carga inicial
    scan_and_ingest()

    rng_demo = random.Random(42)
    demo_tick = 0

    try:
        with Live(
            build_layout(state, _get_gpu_stats()),
            console=console,
            refresh_per_second=round(1 / refresh),
            screen=True,
        ) as live:
            while True:
                # Demo mode: inyectar eventos sintéticos
                if demo_mode:
                    demo_tick += 1
                    if demo_tick % 3 == 0:
                        for ev in generate_demo_events(rng_demo, n=rng_demo.randint(1, 3)):
                            state._process_event(ev, "demo")
                    state.engine_mode = "DEMO"
                else:
                    scan_and_ingest()
                    state.engine_mode = "LIVE"

                gpu = _get_gpu_stats()
                live.update(build_layout(state, gpu))
                time.sleep(refresh)

    except KeyboardInterrupt:
        console.print("\n[dim]VIGÍA Command Center cerrado.[/dim]")


# ══════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="VIGÍA Command Center — Tablero de mando forense en terminal",
    )
    parser.add_argument(
        "--watch", nargs="+", default=["./**/*.jsonl"],
        help="Glob patterns de archivos .jsonl a monitorear",
    )
    parser.add_argument(
        "--refresh", type=float, default=2.0,
        help="Intervalo de refresco en segundos (default: 2.0)",
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Modo demostración: genera eventos sintéticos en tiempo real",
    )
    args = parser.parse_args()

    patterns = args.watch
    # Si el patrón no incluye **.jsonl, agregarlo
    expanded = []
    for p in patterns:
        if not p.endswith(".jsonl") and not p.endswith("*"):
            expanded.append(os.path.join(p, "**/*.jsonl"))
            expanded.append(os.path.join(p, "*.jsonl"))
        else:
            expanded.append(p)

    run_dashboard(
        watch_paths=expanded,
        refresh=args.refresh,
        demo_mode=args.demo,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
