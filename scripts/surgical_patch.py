"""
scripts/surgical_patch.py — Engine de parches quirúrgicos para VIGÍA.

Implementa los cinco invariantes del surgical-patcher:
  1. Anchor exacto y único: conteo == 1 o abort.
  2. Dry-run por defecto.
  3. Backup .bak antes de escribir.
  4. Verificación post-escritura (ast.parse para .py).
  5. Restore automático desde .bak si la verificación falla.

API:
    apply_surgical_patches(path, patches, dry_run=True)

    path:    str | Path — archivo a parchear
    patches: list de (anchor: str, replacement: str)
    dry_run: True  → solo muestra qué cambiaría, no escribe
             False → escribe (backup + verify + restore on fail)

Uso desde CLI (opcional):
    python3 scripts/surgical_patch.py target.py patches.json
    python3 scripts/surgical_patch.py target.py patches.json --apply
"""

from __future__ import annotations

import ast
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


def apply_surgical_patches(
    path: str | Path,
    patches: List[Tuple[str, str]],
    dry_run: bool = True,
) -> None:
    """Aplica una lista de parches anclados sobre un archivo.

    Cada parche es (anchor, replacement). El anchor debe aparecer
    exactamente una vez en el contenido actual — si es 0 o >1, aborta
    con RuntimeError antes de tocar el archivo.

    En dry_run=True imprime el diff conceptual (qué se reemplaza por qué)
    sin escribir nada. En dry_run=False escribe, verifica, y restaura si
    la verificación falla.
    """
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"surgical_patch: archivo no encontrado: {target}")

    content = target.read_text(encoding="utf-8")

    # ── Fase 1: validar todos los anchors antes de tocar el archivo ───────
    for i, (anchor, replacement) in enumerate(patches):
        count = content.count(anchor)
        if count == 0:
            raise RuntimeError(
                f"surgical_patch: anchor {i+1}/{len(patches)} no encontrado "
                f"en {target}.\n"
                f"  Anchor: {repr(anchor[:120])}{'...' if len(anchor) > 120 else ''}\n"
                f"  El archivo puede haber cambiado desde que se escribió el "
                f"parche. No se modificó nada."
            )
        if count > 1:
            raise RuntimeError(
                f"surgical_patch: anchor {i+1}/{len(patches)} aparece {count} "
                f"veces en {target} — ambiguo, no se puede anclar.\n"
                f"  Anchor: {repr(anchor[:120])}{'...' if len(anchor) > 120 else ''}\n"
                f"  Extendé el anchor hasta que sea único."
            )

    # ── Fase 2: dry-run — mostrar qué cambiaría ───────────────────────────
    if dry_run:
        print(f"  [DRY-RUN] {target} — {len(patches)} parche(s):")
        for i, (anchor, replacement) in enumerate(patches):
            a_preview = repr(anchor[:80]) + ("..." if len(anchor) > 80 else "")
            r_preview = repr(replacement[:80]) + ("..." if len(replacement) > 80 else "")
            print(f"    parche {i+1}: {a_preview}")
            print(f"         → {r_preview}")
        return

    # ── Fase 3: aplicar todos los parches sobre el contenido en memoria ───
    new_content = content
    for anchor, replacement in patches:
        new_content = new_content.replace(anchor, replacement, 1)

    # ── Fase 4: backup ────────────────────────────────────────────────────
    bak = target.with_suffix(target.suffix + ".bak")
    shutil.copy2(target, bak)
    print(f"  [BACKUP] {bak}")

    # ── Fase 5: escribir ──────────────────────────────────────────────────
    target.write_text(new_content, encoding="utf-8")
    print(f"  [WRITE]  {target}")

    # ── Fase 6: verificar ─────────────────────────────────────────────────
    written = target.read_text(encoding="utf-8")

    if target.suffix == ".py":
        try:
            ast.parse(written)
        except SyntaxError as exc:
            # Restore inmediato
            shutil.copy2(bak, target)
            raise RuntimeError(
                f"surgical_patch: SyntaxError después de parchear {target}:\n"
                f"  {exc}\n"
                f"  Archivo restaurado desde {bak}."
            )

    # Confirmar que ningún anchor sigue presente (señal de replace fallido)
    for i, (anchor, _) in enumerate(patches):
        if anchor in written:
            shutil.copy2(bak, target)
            raise RuntimeError(
                f"surgical_patch: anchor {i+1} todavía presente en {target} "
                f"después de escribir — el replace no funcionó.\n"
                f"  Archivo restaurado desde {bak}."
            )

    print(f"  [OK]     {target} — sintaxis válida, anchors reemplazados.")


# ── CLI opcional ──────────────────────────────────────────────────────────

def _cli() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Aplicar parches quirúrgicos sobre un archivo."
    )
    parser.add_argument("target", help="Archivo a parchear.")
    parser.add_argument(
        "patches_json",
        help='JSON con lista de [anchor, replacement]: '
             '[["anchor1", "repl1"], ["anchor2", "repl2"]]',
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Escribir cambios (default: dry-run).",
    )
    args = parser.parse_args()

    with open(args.patches_json, encoding="utf-8") as f:
        raw = json.load(f)
    patches = [(p[0], p[1]) for p in raw]

    apply_surgical_patches(args.target, patches, dry_run=not args.apply)


if __name__ == "__main__":
    _cli()
