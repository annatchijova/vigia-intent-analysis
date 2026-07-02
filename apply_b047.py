#!/usr/bin/env python3
"""
apply_b047.py — Aplica los parches anclados de B-047 sobre los cuatro módulos
SIFT cuya fuente o anchor fue verificado en sesión (2026-07-01):

    vigia/sift/macos_forensics.py
    vigia/sift/ios_forensics.py
    vigia/sift/android_forensics.py
    vigia/sift/google_takeout_forensics.py

android_forensics.py fue promovido de "esperado" a VERIFICADO por grep en el
repo vivo (2026-07-01): método en líneas 320-326, idéntico carácter a
carácter al patrón de ios/macos; import de noisy_or_correlated con conteo 1.

El guard y el helper de _math_utils.py van en apply_b047_mathutils.py
(anchors reales contra el grep de la misma sesión). Correr ese primero:
el replacement de acá referencia build_correlation_groups, que debe existir
antes de que cualquier módulo lo importe.

Uso (desde la raíz del repo):
    python3 apply_b047.py            # dry-run: muestra qué cambiaría, no escribe
    python3 apply_b047.py --apply    # escribe (backup .bak + ast.parse + restore on fail)

Requiere el engine compartido scripts/surgical_patch.py (invariantes: conteo
de anchor == 1 o abort, dry-run por defecto, backup, verificación post-write).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ── Engine ────────────────────────────────────────────────────────────────
try:
    from surgical_patch import apply_surgical_patches
except ImportError:
    _scripts = Path(__file__).resolve().parent / "scripts"
    if (_scripts / "surgical_patch.py").is_file():
        sys.path.insert(0, str(_scripts))
        from surgical_patch import apply_surgical_patches
    else:
        sys.exit(
            "[ERROR] No se encontró scripts/surgical_patch.py (el engine "
            "compartido del surgical-patcher).\n"
            "        Correr este script desde la raíz del repo, o aplicar los "
            "anchors de B-047_patchset.md a mano."
        )

# ── Anchors verificados contra la fuente de la sesión 2026-07-01 ─────────
# El engine aborta si el conteo de un anchor != 1, así que cualquier drift
# del archivo desde entonces falla en seco en vez de parchear mal.

_IMPORT_ANCHOR = "from vigia.sift._math_utils import noisy_or_correlated"
_IMPORT_REPLACEMENT = (
    "from vigia.sift._math_utils import build_correlation_groups, "
    "noisy_or_correlated"
)

# Método idéntico carácter a carácter en macos_forensics.py, ios_forensics.py
# y android_forensics.py (este último verificado por grep en el repo vivo,
# líneas 320-326, sesión 2026-07-01).
_LIST_METHOD_ANCHOR = '''    def _build_correlation_groups(self) -> List[List[int]]:
        """Group correlated findings by corr_group tag (P0-003 fix)."""
        groups: Dict[str, List[int]] = {}
        for i, f in enumerate(self._findings):
            if f.corr_group:
                groups.setdefault(f.corr_group, []).append(i)
        return [idxs for idxs in groups.values() if len(idxs) >= 2]'''

_DELEGATE_REPLACEMENT = '''    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; replaces List[List[int]] format)."""
        return build_correlation_groups([f.corr_group for f in self._findings])'''

# Implementación de referencia de takeout (correcta) — se reemplaza por la
# delegación porque la semántica canónica pasa a vivir en el helper.
_TAKEOUT_METHOD_ANCHOR = '''    def _build_correlation_groups(self) -> Dict[int, set]:
        """Build correlation map in the format noisy_or_correlated expects:
        Dict[int, Set[int]] where each key maps to its correlated peers.

        NOTE: Android/iOS/macOS _build_correlation_groups return List[List[int]]
        which is a latent bug — noisy_or_correlated expects Dict[int, Set[int]].
        This module uses the correct format.
        """
        tag_groups: Dict[str, List[int]] = {}
        for i, f in enumerate(self._findings):
            if f.corr_group:
                tag_groups.setdefault(f.corr_group, []).append(i)
        result: Dict[int, set] = {}
        for indices in tag_groups.values():
            if len(indices) < 2:
                continue
            for idx in indices:
                peers = {j for j in indices if j != idx}
                if idx in result:
                    result[idx] |= peers
                else:
                    result[idx] = peers
        return result'''

_TAKEOUT_DELEGATE_REPLACEMENT = '''    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; canonical semantics live there)."""
        return build_correlation_groups([f.corr_group for f in self._findings])'''

# ── Patch sets por archivo ────────────────────────────────────────────────

PATCH_SETS: dict[str, list[tuple[str, str]]] = {
    "vigia/sift/macos_forensics.py": [
        (_IMPORT_ANCHOR, _IMPORT_REPLACEMENT),
        (_LIST_METHOD_ANCHOR, _DELEGATE_REPLACEMENT),
    ],
    "vigia/sift/ios_forensics.py": [
        (_IMPORT_ANCHOR, _IMPORT_REPLACEMENT),
        (_LIST_METHOD_ANCHOR, _DELEGATE_REPLACEMENT),
    ],
    "vigia/sift/android_forensics.py": [
        (_IMPORT_ANCHOR, _IMPORT_REPLACEMENT),
        (_LIST_METHOD_ANCHOR, _DELEGATE_REPLACEMENT),
    ],
    "vigia/sift/google_takeout_forensics.py": [
        (_IMPORT_ANCHOR, _IMPORT_REPLACEMENT),
        (_TAKEOUT_METHOD_ANCHOR, _TAKEOUT_DELEGATE_REPLACEMENT),
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B-047: delegar _build_correlation_groups al helper "
                    "compartido (dry-run por defecto)."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Escribir los cambios (default: dry-run, solo mostrar).",
    )
    args = parser.parse_args()
    dry = not args.apply

    print(f"[B-047] Modo: {'DRY-RUN (no escribe)' if dry else 'APPLY'}\n")

    failures = 0
    for path, patches in PATCH_SETS.items():
        if not Path(path).is_file():
            print(f"[ERROR] No existe: {path} — ¿estás en la raíz del repo?")
            failures += 1
            continue
        print(f"── {path} ({len(patches)} parches) " + "─" * 20)
        try:
            apply_surgical_patches(path, patches, dry_run=dry)
        except Exception as exc:  # el engine ya reporta; esto evita medio-aplicar
            print(f"[ERROR] {path}: {exc}")
            failures += 1
        print()

    if failures:
        print(f"[B-047] {failures} archivo(s) con error — nada más que revisar "
              f"eso antes de reintentar. Los anchors no negocian (count == 1).")
        return 1
    if dry:
        print("[B-047] Dry-run OK. Revisar la salida y correr con --apply.")
    else:
        print("[B-047] Aplicado a los 4 módulos. Si aún no corriste "
              "apply_b047_mathutils.py --apply, correlo ahora (el helper "
              "importado debe existir). Después:\n"
              "  PYTHONPATH=$(pwd) python3 -m pytest "
              "vigia/tests/test_b047_correlation_groups.py -v --no-cov")
    return 0


if __name__ == "__main__":
    sys.exit(main())
