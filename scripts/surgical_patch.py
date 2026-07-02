"""
scripts/surgical_patch.py — Engine de parches quirúrgicos para VIGÍA. v2.

Implementa los cinco invariantes del surgical-patcher:
  1. Anchor exacto y único: conteo == 1 o abort (con excepción de idempotencia,
     ver ENG-001).
  2. Dry-run por defecto.
  3. Backup .bak antes de escribir.
  4. Verificación post-escritura (ast.parse para .py + presencia del
     replacement).
  5. Restore automático desde .bak si la verificación falla.

CHANGELOG
─────────
ENG-001 (v2, 2026-07-01) — Falso positivo en la verificación post-escritura
con parches ADITIVOS (replacement que contiene al anchor completo, p. ej.
"bloque existente + bloque nuevo"). La v1 verificaba `anchor in written` y
concluía que el replace había fallado cuando el anchor seguía presente —
pero en un parche aditivo el anchor DEBE seguir presente. Resultado: la v1
deshacía (restore) parches correctos. Detectado aplicando B-048 sobre
vigia_agent.py (el parche del shim, sustitutivo, pasó; el del agente,
aditivo, fue revertido por error).

Fix v2, dos cambios:
  a) Verificación por REPLACEMENT: post-escritura se exige
     `replacement in written` para cada parche aplicado. Solo si el anchor
     NO es substring de su replacement (parche sustitutivo) se exige además
     `anchor not in written`.
  b) Idempotencia detectada: si en fase 1 un anchor cuenta 0 PERO su
     replacement ya está presente en el contenido, el parche se marca
     [SKIP — ya aplicado] en vez de abortar. Esto permite re-ejecutar un
     script de parches tras un fallo parcial sin drama. Nota: la detección
     asume replacements largos y distintivos (como los de esta casa); un
     replacement genérico y corto podría producir un skip erróneo.

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


def _preview(s: str, n: int = 80) -> str:
    return repr(s[:n]) + ("..." if len(s) > n else "")


def apply_surgical_patches(
    path: str | Path,
    patches: List[Tuple[str, str]],
    dry_run: bool = True,
) -> None:
    """Aplica una lista de parches anclados sobre un archivo.

    Cada parche es (anchor, replacement). Estados posibles por parche en la
    fase de validación:
      - PENDING: anchor cuenta exactamente 1 → se aplicará.
      - SKIP:    anchor cuenta 0 pero el replacement ya está en el archivo
                 → ya aplicado en una corrida anterior (ENG-001 b).
      - ERROR:   anchor cuenta 0 sin replacement presente (drift del
                 archivo), o cuenta >1 (ambiguo). Aborta sin tocar nada.
    """
    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"surgical_patch: archivo no encontrado: {target}")

    content = target.read_text(encoding="utf-8")

    # ── Fase 1: clasificar todos los parches antes de tocar el archivo ────
    pending: List[Tuple[int, str, str]] = []
    for i, (anchor, replacement) in enumerate(patches):
        count = content.count(anchor)
        if count == 1:
            pending.append((i, anchor, replacement))
        elif count == 0 and replacement in content:
            print(f"  [SKIP]   parche {i+1}/{len(patches)} ya aplicado "
                  f"(replacement presente, anchor ausente).")
        elif count == 0:
            raise RuntimeError(
                f"surgical_patch: anchor {i+1}/{len(patches)} no encontrado "
                f"en {target} y su replacement tampoco está presente.\n"
                f"  Anchor: {_preview(anchor, 120)}\n"
                f"  El archivo cambió desde que se escribió el parche. "
                f"No se modificó nada."
            )
        else:
            raise RuntimeError(
                f"surgical_patch: anchor {i+1}/{len(patches)} aparece {count} "
                f"veces en {target} — ambiguo, no se puede anclar.\n"
                f"  Anchor: {_preview(anchor, 120)}\n"
                f"  Extendé el anchor hasta que sea único."
            )

    if not pending:
        print(f"  [OK]     {target} — nada pendiente "
              f"(todos los parches ya aplicados).")
        return

    # ── Fase 2: dry-run — mostrar qué cambiaría ───────────────────────────
    if dry_run:
        print(f"  [DRY-RUN] {target} — {len(pending)} parche(s) pendiente(s):")
        for i, anchor, replacement in pending:
            print(f"    parche {i+1}: {_preview(anchor)}")
            print(f"         → {_preview(replacement)}")
        return

    # ── Fase 3: aplicar los pendientes sobre el contenido en memoria ──────
    new_content = content
    for _, anchor, replacement in pending:
        new_content = new_content.replace(anchor, replacement, 1)

    # ── Fase 4: backup ────────────────────────────────────────────────────
    bak = target.with_suffix(target.suffix + ".bak")
    shutil.copy2(target, bak)
    print(f"  [BACKUP] {bak}")

    # ── Fase 5: escribir ──────────────────────────────────────────────────
    target.write_text(new_content, encoding="utf-8")
    print(f"  [WRITE]  {target}")

    # ── Fase 6: verificar (ENG-001 a) ─────────────────────────────────────
    written = target.read_text(encoding="utf-8")

    if target.suffix == ".py":
        try:
            ast.parse(written)
        except SyntaxError as exc:
            shutil.copy2(bak, target)
            raise RuntimeError(
                f"surgical_patch: SyntaxError después de parchear {target}:\n"
                f"  {exc}\n"
                f"  Archivo restaurado desde {bak}."
            )

    for i, anchor, replacement in pending:
        if replacement not in written:
            shutil.copy2(bak, target)
            raise RuntimeError(
                f"surgical_patch: replacement del parche {i+1} ausente en "
                f"{target} después de escribir — el replace no funcionó.\n"
                f"  Archivo restaurado desde {bak}."
            )
        # Solo los parches SUSTITUTIVOS exigen la desaparición del anchor.
        # En un parche aditivo (anchor ⊂ replacement) el anchor sigue ahí
        # por diseño — ese era exactamente el falso positivo de la v1.
        if anchor not in replacement and anchor in written:
            shutil.copy2(bak, target)
            raise RuntimeError(
                f"surgical_patch: anchor {i+1} (sustitutivo) todavía presente "
                f"en {target} después de escribir.\n"
                f"  Archivo restaurado desde {bak}."
            )

    print(f"  [OK]     {target} — sintaxis válida, "
          f"{len(pending)} parche(s) verificado(s).")


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
