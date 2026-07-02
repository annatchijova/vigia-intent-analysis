#!/usr/bin/env python3
"""
apply_b048.py — Cablea MacOSForensicsAnalyzer al pipeline (B-048).

Mismo patrón que B-045 (Android/iOS) y B-046 (Takeout), con dos guards
adicionales que el calco puro no tiene, motivados por una colisión real de
markers detectada durante el diseño del parche:

  COLISIÓN: "History.db" existe en _IOS_MARKER_FILES y en
  _MACOS_MARKER_FILES. Toda evidencia macOS real tiene un Safari History.db,
  así que el calco puro dispararía ambos engines sobre el mismo directorio y
  ambos procesarían los mismos artefactos Safari → doble conteo sistemático.

  Guard 1 (agente): macOS se detecta con
      _MACOS_MARKER_FILES - _IOS_MARKER_FILES
  (computado desde los imports, sin duplicar datos). Evita que evidencia iOS
  pura dispare el detector macOS. Riesgo residual documentado: extracciones
  iOS completas con TCC.db (que no está en _IOS_MARKER_FILES) podrían
  disparar macOS — aceptado y registrado en B-048.

  Guard 2 (shim): si ios_evidence_path == macos_evidence_path, corre solo el
  engine macOS con warning en el log. Corta el doble conteo en el caso
  principal (evidencia macOS genuina que matchea ambos detectores).

Parches (3), todos anclados verbatim contra los fragmentos del repo vivo
pegados en sesión 2026-07-01:

  1. vigia_agent.py::_build_orchestrator_kwargs() — detección de markers
     macOS después del bloque B-046.
  2. sift_orchestrator.py (shim)::_analyze_mobile() — guard de precedencia
     antes del bloque iOS.
  3. sift_orchestrator.py (shim)::_analyze_mobile() — bloque de análisis
     macOS después del bloque Takeout.

Uso (desde la raíz del repo, venv activado):
    python3 apply_b048.py            # dry-run
    python3 apply_b048.py --apply    # escribe (backup .bak + ast.parse + restore)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from surgical_patch import apply_surgical_patches
except ImportError:
    _scripts = Path(__file__).resolve().parent / "scripts"
    if (_scripts / "surgical_patch.py").is_file():
        sys.path.insert(0, str(_scripts))
        from surgical_patch import apply_surgical_patches
    else:
        sys.exit(
            "[ERROR] No se encontró scripts/surgical_patch.py.\n"
            "        Correr desde la raíz del repo."
        )

# ── Parche 1: detección en vigia_agent.py ─────────────────────────────────
# Anchor: el bloque B-046 completo (único por el literal _TAKEOUT_MARKER_FILES).

_AGENT_ANCHOR = '''        # B-046: detect Google Takeout evidence directories by marker files
        try:
            from vigia.sift.google_takeout_forensics import _TAKEOUT_MARKER_FILES
            if all_names & _TAKEOUT_MARKER_FILES:
                kwargs["takeout_evidence_path"] = str(evidence_path)
        except ImportError:
            pass'''

_AGENT_REPLACEMENT = '''        # B-046: detect Google Takeout evidence directories by marker files
        try:
            from vigia.sift.google_takeout_forensics import _TAKEOUT_MARKER_FILES
            if all_names & _TAKEOUT_MARKER_FILES:
                kwargs["takeout_evidence_path"] = str(evidence_path)
        except ImportError:
            pass
        # B-048: detect macOS evidence directories by marker files.
        # Collision guard: History.db (Safari) also lives in _IOS_MARKER_FILES,
        # and every real macOS evidence set has one — detecting macOS on shared
        # names would run both engines over the same artifacts (double count).
        # macOS therefore requires a marker NOT shared with iOS. Residual risk
        # (documented in B-048): full iOS extractions containing TCC.db may
        # still trigger this detector; the shim precedence guard handles the
        # same-directory case.
        try:
            from vigia.sift.macos_forensics import _MACOS_MARKER_FILES
            from vigia.sift.ios_forensics import _IOS_MARKER_FILES
            if all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES):
                kwargs["macos_evidence_path"] = str(evidence_path)
        except ImportError:
            pass'''

# ── Parche 2: guard de precedencia en el shim (antes del bloque iOS) ──────
# Anchor: la apertura del bloque iOS (único por el literal ios_evidence_path
# en un .get seguido del if).

_SHIM_IOS_ANCHOR = '''        ios_path = kwargs.get("ios_evidence_path")
        if ios_path:'''

_SHIM_IOS_REPLACEMENT = '''        ios_path = kwargs.get("ios_evidence_path")
        # B-048 precedence: if the same directory also matched macOS strong
        # markers, run only the macOS engine — shared Safari artifacts
        # (History.db) would otherwise be processed and counted by both.
        if ios_path and ios_path == kwargs.get("macos_evidence_path"):
            logger.warning(
                "[SIFT_SHIM] iOS engine skipped for %s: directory also matched "
                "macOS strong markers; macOS engine takes precedence to avoid "
                "double-counting shared Safari artifacts (B-048).",
                ios_path,
            )
            ios_path = None
        if ios_path:'''

# ── Parche 3: bloque macOS en el shim (después del bloque Takeout) ────────
# Anchor: cierre del bloque Takeout + return del método (único por el mensaje
# de error de GoogleTakeoutForensicsAnalyzer).

_SHIM_MACOS_ANCHOR = '''            except Exception as e:
                logger.error("[SIFT_SHIM] GoogleTakeoutForensicsAnalyzer failed: %s", e)

        return signals'''

_SHIM_MACOS_REPLACEMENT = '''            except Exception as e:
                logger.error("[SIFT_SHIM] GoogleTakeoutForensicsAnalyzer failed: %s", e)

        # B-048: macOS forensics
        macos_path = kwargs.get("macos_evidence_path")
        if macos_path:
            try:
                from vigia.sift.macos_forensics import MacOSForensicsAnalyzer
                analyzer = MacOSForensicsAnalyzer()
                result = analyzer.analyze(Path(macos_path))
                sig = result.to_signal()
                if sig and (sig.z_score > 0 or result.findings):
                    sig_dict = {
                        "tool": sig.tool_name,
                        "z_score": sig.z_score,
                        "confidence": sig.confidence,
                        "value": sig.value,
                        "metadata": sig.metadata,
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] macOS engine: %d findings, z=%.2f",
                        len(result.findings), sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] MacOSForensicsAnalyzer failed: %s", e)

        return signals'''

PATCH_SETS: dict[str, list[tuple[str, str]]] = {
    "vigia_agent.py": [
        (_AGENT_ANCHOR, _AGENT_REPLACEMENT),
    ],
    "sift_orchestrator.py": [
        (_SHIM_IOS_ANCHOR, _SHIM_IOS_REPLACEMENT),
        (_SHIM_MACOS_ANCHOR, _SHIM_MACOS_REPLACEMENT),
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B-048: cablear MacOSForensicsAnalyzer (dry-run por defecto)."
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dry = not args.apply

    print(f"[B-048] Modo: {'DRY-RUN (no escribe)' if dry else 'APPLY'}\n")

    failures = 0
    for path, patches in PATCH_SETS.items():
        if not Path(path).is_file():
            print(f"[ERROR] No existe: {path} — ¿estás en la raíz del repo?")
            failures += 1
            continue
        print(f"── {path} ({len(patches)} parche(s)) " + "─" * 20)
        try:
            apply_surgical_patches(path, patches, dry_run=dry)
        except Exception as exc:
            print(f"[ERROR] {path}: {exc}")
            failures += 1
        print()

    if failures:
        print(f"[B-048] {failures} archivo(s) con error — revisar antes de reintentar.")
        return 1
    if dry:
        print("[B-048] Dry-run OK. Revisar la salida y correr con --apply.")
    else:
        print("[B-048] Aplicado. Smoke test end-to-end:\n"
              "  python3 smoke_b048.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
