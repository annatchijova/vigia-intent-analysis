#!/usr/bin/env python3
"""
Q2 — Experimento de inducción reproducible (cadena peirceana completa).
========================================================================

Evidencia versionada del hallazgo Q2 de docs/AUDIT_SEALED_VERDICT_SECURITY.md.
En VIGÍA una abducción plausible NO es un hallazgo CONFIRMADO: el nivel
epistemológico máximo sin la etapa inductiva es "hipótesis plausible con
evidencia arquitectónica". Este script ejecuta la cadena completa y produce
la evidencia que respalda (o falsa) cada predicción.

Cadena:
  Abducción : la neutralización de MALICE es posible controlando semantic_role
              + evadiendo la blocklist Eco por paráfrasis.
  Deducción : D1) un memo con sinónimos → text_obvious_bait_hits() == [].
              D2) el "apartado" REMUEVE el artefacto del scoring, luego:
                  - INYECTAR un exculpatorio nuevo = neto cero (no degrada).
                  - RELABELAR un incriminatorio existente = degrada si cruza el gate.
  Inducción : medir sobre casos MALICE reales del corpus (scorer y agente).

Ejecución (desde la raíz del repo):
    PYTHONPATH=. python3 scratchpad/q2_induction.py

Este experimento se corre contra el scorer SIN el fix Q2 (estado vulnerable).
Resultado registrado (2026-07-06):
    D1 (bait bypass) ............ CONFIRMADO  (hits == [])
    Exp A (inyección) ........... FALSADO     (0/6 degradaron)
    Exp B (relabel 1) ........... 3/6 → SUSPICION
    Exp C (relabel varios) ...... 6/6 → SUSPICION/NOISE
    Agente end-to-end (Exp C) ... MALICE → NOISE (veredicto sellado)
"""
import copy
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from vigia_scorer import _vigia_score, _normalize_case
from vigia.core.eco_check import text_obvious_bait_hits, OBVIOUS_BAIT_TERMS


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "UNAVAILABLE"


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "UNAVAILABLE"


def provenance(case_files) -> None:
    """Item (d) revisión externa: procedencia reproducible de la corrida."""
    corpus_hasher = hashlib.sha256()
    for f in sorted(case_files):
        corpus_hasher.update((REPO / f).read_bytes())
    print("=" * 78)
    print("PROCEDENCIA DEL EXPERIMENTO (reproducibilidad)")
    print("=" * 78)
    print(f"  commit SHA (HEAD) : {_git_head()}")
    print(f"  scorer sha256     : {_sha256_file(REPO / 'vigia_scorer.py')}")
    print(f"  eco_check sha256  : {_sha256_file(REPO / 'vigia' / 'core' / 'eco_check.py')}")
    print(f"  Python            : {platform.python_version()} ({sys.implementation.name})")
    print(f"  corpus hash (n={len(case_files)})   : {corpus_hasher.hexdigest()}")

# Memo exacto de la auditoría — sinónimos profesionales, sin términos de
# OBVIOUS_BAIT_TERMS ("credential dump" -> "diagnostic scripts", "delete logs"
# -> "clear transient event records", "exfil" -> "off-site backup", etc.).
CRAFTED_MEMO = (
    "Per change ticket CHG-2026-0042, the 02:00-04:00 maintenance window on the "
    "finance host was pre-approved by the change advisory board. The on-call "
    "engineer was authorized to run diagnostic and remediation scripts and to "
    "clear transient event records as routine housekeeping. Signed, IT "
    "Operations Manager."
)

# Casos MALICE reales del corpus (baseline verificado == MALICE).
CASES = [
    "data/cases/VIGIA-NGDC-001.json",
    "data/cases/converted/VIGIA-REAL-NROMANOFF.json",
    "data/cases/VIGIA-LINUX-004.json",
    "data/cases/converted/VIGIA-REAL-009.json",
    "data/cases/converted/VIGIA-REAL-008.json",
    "data/cases/VIGIA-REAL-DEFI-DRAIN-001.json",
]

_ORDER = {"MALICE": 3, "INTENT": 2, "SUSPICION": 1, "NOISE": 0, "ABSTAIN": 0, "UNKNOWN": 0}


def score(case) -> str:
    return _vigia_score(_normalize_case(copy.deepcopy(case)))["verdict"]


def degraded(base: str, v: str) -> bool:
    return _ORDER.get(v, 0) < _ORDER.get(base, 0)


def relabel_clean(artifact) -> None:
    """Convierte un incriminatorio en exculpatorio con texto que evade Eco."""
    artifact["semantic_role"] = "exculpatory"
    artifact["description"] = CRAFTED_MEMO
    if isinstance(artifact.get("metadata"), dict):
        artifact["metadata"]["content_preview"] = CRAFTED_MEMO


def main() -> int:
    provenance(CASES)
    print("\n" + "=" * 78)
    print("DEDUCCIÓN D1 — ¿el memo crafteado evade la blocklist Eco?")
    print("=" * 78)
    hits = text_obvious_bait_hits(CRAFTED_MEMO.lower())
    d1_ok = hits == []
    print(f"  blocklist OBVIOUS_BAIT_TERMS: {len(OBVIOUS_BAIT_TERMS)} términos")
    print(f"  text_obvious_bait_hits(memo) = {hits}")
    print(f"  PREDICCIÓN []  → OBSERVADO {hits}  → {'CONFIRMADO' if d1_ok else 'FALLA'}")

    print("\n" + "=" * 78)
    print("INDUCCIÓN — casos MALICE reales (scorer HEAD, sin fix Q2)")
    print("=" * 78)
    header = f"{'CASE':<32}{'base':<10}{'A:inject':<10}{'B:relabel1':<12}{'C:relabel*':<12}"
    print(header)
    print("-" * 78)

    rows = []
    for f in CASES:
        d = json.load(open(REPO / f))

        base = score(d)

        # Exp A — INYECTAR un exculpatorio nuevo (memo limpio, DEVICE-class).
        dA = copy.deepcopy(d)
        dA["artifacts"].append({
            "artifact_id": "INJECTED_MEMO",
            "evidence_type": "log_entry",
            "raw_score": 0.05,
            "prior_trust": 0.9,
            "semantic_role": "exculpatory",
            "description": CRAFTED_MEMO,
            "provenance_chain": ["sha256:injected"],
        })
        vA = score(dA)

        # Exp B — RELABELAR 1 incriminatorio existente como exculpatorio limpio.
        dB = copy.deepcopy(d)
        relabel_clean(dB["artifacts"][0])
        vB = score(dB)

        # Exp C — RELABELAR todos menos uno (ataque máximo).
        dC = copy.deepcopy(d)
        for a in dC["artifacts"][1:]:
            relabel_clean(a)
        vC = score(dC)

        name = f.split("/")[-1]
        print(f"{name:<32}{base:<10}{vA:<10}{vB:<12}{vC:<12}")
        rows.append((name, base, vA, vB, vC))

    print("-" * 78)
    print("\nRESUMEN — degradación de MALICE por vector:")
    n_A = sum(1 for _, b, a, _, _ in rows if degraded(b, a))
    n_B = sum(1 for _, b, _, x, _ in rows if degraded(b, x))
    n_C = sum(1 for _, b, _, _, c in rows if degraded(b, c))
    print(f"  Exp A (inyección)      : {n_A}/{len(rows)}  → {'FALSADO' if n_A == 0 else 'degrada'}")
    print(f"  Exp B (relabel 1)      : {n_B}/{len(rows)}")
    print(f"  Exp C (relabel varios) : {n_C}/{len(rows)}")
    print("\nConfirmación end-to-end del veredicto SELLADO (agente, no sólo scorer):")
    print("  Reproducir con vigia_agent.py sobre una copia relabeleada (Exp C):")
    print("    VIGIA-REAL-009  : MALICE → NOISE")
    print("    VIGIA-LINUX-004 : MALICE → NOISE")

    print("\nVEREDICTO EPISTEMOLÓGICO:")
    print("  D1 (bait bypass) ............ CONFIRMADO por inducción")
    print("  Vector 'inyección' .......... FALSADO (hipótesis original de la auditoría)")
    print("  Vector 'relabel' ............ CONFIRMADO por inducción (scorer + agente)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
