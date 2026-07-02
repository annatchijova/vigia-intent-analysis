#!/usr/bin/env python3
"""
smoke_b048.py — Smoke test end-to-end del wiring de macOS (B-048). v2.

CHANGELOG v2 (2026-07-01): la v1 generaba fixture y bundle en /tmp; el
agente rechaza --output fuera del working directory con
"[FATAL] Output path escapes working directory" — un guard de seguridad
legítimo, no un bug. Ahora todo vive DENTRO del repo, en results/b048_smoke/
(fixture + bundle, rutas relativas). Si el smoke PASA, el directorio se
borra solo; si FALLA, se conserva para inspección. No commitear
results/b048_smoke/ si queda.

Qué hace:
  1. Genera un fixture sintético de evidencia macOS con los schemas SQLite
     reales que macos_forensics.py consulta:
       - SystemVersion.plist            (identificación del sistema)
       - Users/anna/Library/Safari/History.db
             history_items + history_visits, con DOS URLs que matchean
             SUSPICIOUS_SEARCH_PATTERNS y comparten corr_group
             "browser_suspicious" — de paso ejercita el path correlacionado
             de B-047 en producción (pre-B-047 este mismo fixture habría
             crasheado con AttributeError en noisy_or_correlated).
       - private/var/db/com.apple.LaunchServices.QuarantineEventsV2
             LSQuarantineEvent con un download vía curl
             (QUARANTINE_CLI_DOWNLOAD).
     El History.db va deliberadamente bajo .../Safari/ porque
     _analyze_safari tiene el guard `if "Safari" not in str(db): continue`.

  2. Corre el pipeline REAL por subprocess:
         python3 vigia_agent.py --evidence <fixture> --case-id B048-SMOKE ...
     Nada de importar internals — se valida la integración completa.

  3. Verifica en el bundle sellado:
       - PASS  si aparece la señal MACOS_FORENSICS.
       - PASS  si NO aparece IOS_FORENSICS (el fixture tiene un History.db,
               que matchea _IOS_MARKER_FILES: sin el guard de precedencia
               de B-048, el engine iOS correría y duplicaría los findings).
       - Falla explícita (exit != 0) en cualquier otro caso.

Uso (desde la raíz del repo, venv activado):
    python3 smoke_b048.py
"""

from __future__ import annotations

import json
import os
import plistlib
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

# Core Data epoch (2001-01-01) — visit_time de Safari usa este epoch.
# 730000000 s desde 2001 ≈ 2024-02. Valor arbitrario pero plausible.
_COREDATA_TS = 730000000

SMOKE_DIR = Path("results") / "b048_smoke"
FIXTURE_DIR = SMOKE_DIR / "fixture"
BUNDLE_PATH = SMOKE_DIR / "B048-SMOKE_bundle.json"


def build_fixture(root: Path) -> Path:
    """Construye el directorio de evidencia macOS sintética. Devuelve root."""

    # 1. SystemVersion.plist
    sv = root / "System" / "Library" / "CoreServices"
    sv.mkdir(parents=True)
    with open(sv / "SystemVersion.plist", "wb") as f:
        plistlib.dump(
            {"ProductVersion": "13.6", "ProductBuildVersion": "22G120",
             "ProductName": "macOS"},
            f,
        )

    # 2. Safari History.db — schema mínimo que _analyze_safari consulta:
    #    history_items(id, url) JOIN history_visits(history_item, title,
    #    visit_time). Dos URLs suspicious con el mismo corr_group para
    #    ejercitar el path correlacionado (B-047).
    safari = root / "Users" / "anna" / "Library" / "Safari"
    safari.mkdir(parents=True)
    conn = sqlite3.connect(safari / "History.db")
    conn.executescript(
        """
        CREATE TABLE history_items (id INTEGER PRIMARY KEY, url TEXT);
        CREATE TABLE history_visits (
            history_item INTEGER, title TEXT, visit_time REAL
        );
        """
    )
    rows = [
        (1, "https://search.example/results?q=how+to+hack+wifi",
         "how to hack wifi - Search"),
        (2, "https://search.example/results?q=delete+history+permanently+mac",
         "delete history permanently mac - Search"),
        (3, "https://recipes.example/milanesas-de-seitan",
         "Milanesas de seitán"),
    ]
    for item_id, url, title in rows:
        conn.execute("INSERT INTO history_items (id, url) VALUES (?, ?)",
                     (item_id, url))
        conn.execute(
            "INSERT INTO history_visits (history_item, title, visit_time) "
            "VALUES (?, ?, ?)",
            (item_id, title, _COREDATA_TS + item_id),
        )
    conn.commit()
    conn.close()

    # 3. QuarantineEventsV2 — schema real de LSQuarantineEvent; un download
    #    por curl dispara QUARANTINE_CLI_DOWNLOAD.
    qdir = root / "private" / "var" / "db"
    qdir.mkdir(parents=True)
    conn = sqlite3.connect(qdir / "com.apple.LaunchServices.QuarantineEventsV2")
    conn.executescript(
        """
        CREATE TABLE LSQuarantineEvent (
            LSQuarantineEventIdentifier TEXT,
            LSQuarantineTimeStamp REAL,
            LSQuarantineAgentBundleIdentifier TEXT,
            LSQuarantineAgentName TEXT,
            LSQuarantineDataURLString TEXT,
            LSQuarantineSenderName TEXT,
            LSQuarantineSenderAddress TEXT,
            LSQuarantineTypeNumber INTEGER,
            LSQuarantineOriginTitle TEXT,
            LSQuarantineOriginURLString TEXT,
            LSQuarantineOriginAlias BLOB
        );
        """
    )
    conn.execute(
        "INSERT INTO LSQuarantineEvent (LSQuarantineEventIdentifier, "
        "LSQuarantineTimeStamp, LSQuarantineAgentName, "
        "LSQuarantineDataURLString) VALUES (?, ?, ?, ?)",
        ("B048-SMOKE-EVT-1", float(_COREDATA_TS), "curl",
         "https://files.example/tool.sh"),
    )
    conn.commit()
    conn.close()

    return root


def main() -> int:
    repo = Path.cwd()
    if not (repo / "vigia_agent.py").is_file():
        print("[SMOKE B-048] Correr desde la raíz del repo "
              "(no encuentro vigia_agent.py).")
        return 2

    # Fixture y bundle DENTRO del repo — el agente rechaza outputs fuera del
    # working directory (guard de seguridad, ver changelog v2).
    if SMOKE_DIR.exists():
        shutil.rmtree(SMOKE_DIR)
    FIXTURE_DIR.mkdir(parents=True)
    build_fixture(FIXTURE_DIR)
    print(f"[SMOKE B-048] Fixture: {FIXTURE_DIR}")

    env = dict(os.environ, PYTHONPATH=str(repo))
    cmd = [
        sys.executable, "vigia_agent.py",
        "--evidence", str(FIXTURE_DIR),
        "--case-id", "B048-SMOKE",
        "--output", str(BUNDLE_PATH),
    ]
    print(f"[SMOKE B-048] Ejecutando: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=300, env=env)

    # El exit code del agente NO es el criterio de éxito: 0 = clean es
    # correcto si z < threshold (mismo caso que Owl-Android); 3 = INTENT/
    # SUSPICION también es plausible según la señal. El criterio es la
    # presencia/ausencia de las señales en el bundle.
    print(f"[SMOKE B-048] vigia_agent exit code: {proc.returncode}")

    bundle_text = ""
    if BUNDLE_PATH.is_file():
        bundle_text = BUNDLE_PATH.read_text(encoding="utf-8")
    else:
        print("[SMOKE B-048] --output no produjo archivo; stdout del agente:")
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        candidates = sorted(repo.glob("results/**/B048-SMOKE*"),
                            key=lambda p: p.stat().st_mtime, reverse=True)
        candidates = [c for c in candidates if c.is_file()]
        if candidates:
            print(f"[SMOKE B-048] Bundle encontrado en: {candidates[0]}")
            bundle_text = candidates[0].read_text(encoding="utf-8")
        else:
            print("[SMOKE B-048] FAIL — no se encontró ningún bundle. "
                  "Revisar stdout/stderr arriba. Fixture conservado en "
                  f"{FIXTURE_DIR} para inspección.")
            return 1

    failures = []

    if "MACOS_FORENSICS" in bundle_text:
        print("[SMOKE B-048] PASS — señal MACOS_FORENSICS presente.")
        try:
            data = json.loads(bundle_text)
            blob = json.dumps(data)
            idx = blob.find("MACOS_FORENSICS")
            print(f"[SMOKE B-048]   contexto: ...{blob[max(0, idx-40):idx+160]}...")
        except (json.JSONDecodeError, ValueError):
            pass
    else:
        failures.append(
            "señal MACOS_FORENSICS AUSENTE — el wiring no funcionó "
            "(¿se aplicó el parche de vigia_agent.py? Revisar que "
            "apply_b048.py haya reportado OK, no ERROR, para ese archivo)"
        )

    if "IOS_FORENSICS" in bundle_text:
        failures.append(
            "señal IOS_FORENSICS PRESENTE — doble conteo: el guard de "
            "precedencia macOS>iOS no está actuando (el fixture tiene un "
            "History.db que matchea _IOS_MARKER_FILES)"
        )
    else:
        print("[SMOKE B-048] PASS — sin señal IOS_FORENSICS (precedencia OK).")

    if failures:
        for f in failures:
            print(f"[SMOKE B-048] FAIL — {f}")
        print(f"[SMOKE B-048] Artefactos conservados para inspección en "
              f"{SMOKE_DIR}/ (no commitear).")
        return 1

    print("[SMOKE B-048] OK — wiring macOS validado end-to-end. "
          f"Limpiando {SMOKE_DIR}/ ...")
    shutil.rmtree(SMOKE_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
