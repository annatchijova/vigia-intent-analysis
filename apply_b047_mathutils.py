#!/usr/bin/env python3
"""
apply_b047_mathutils.py — Parches de B-047 sobre vigia/sift/_math_utils.py:

    1. Guard fail-loud en noisy_or_correlated(): rechaza correlation_groups
       que no sea dict (o None), en vez de fallar más abajo con un
       AttributeError opaco cuando el formato viejo (List[List[int]]) llega.
    2. Helper canónico build_correlation_groups() — la implementación única
       de la que van a depender los 4 módulos SIFT (macos, ios, android,
       takeout) en vez de tener 4 copias.

Anchors verificados contra el grep de la sesión (2026-07-01):

    grep -n -B 2 -A 30 "def noisy_or_correlated" vigia/sift/_math_utils.py

Firma real confirmada:
    def noisy_or_correlated(
        severities: List[Fraction],
        correlation_groups: Optional[Dict[int, Set[int]]] = None,
        penalty: Fraction = Fraction(15, 100),
        penalty_map: Optional[Dict[str, Fraction]] = None,
    ) -> Fraction:

Modo de fallo pre-fix confirmado (B-047): con correlation_groups como lista
no vacía, `correlation_groups.items()` (línea con `for idx, group in
sorted(correlation_groups.items())`) revienta con
AttributeError: 'list' object has no attribute 'items'.
Fail-loud accidental — no corrupción silenciosa — pero sin mensaje útil ni
referencia al bug. El guard lo vuelve explícito.

Uso (desde la raíz del repo, con el venv activado):
    python3 apply_b047_mathutils.py            # dry-run
    python3 apply_b047_mathutils.py --apply    # escribe

Requiere scripts/surgical_patch.py (mismo engine que apply_b047.py).
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

TARGET = "vigia/sift/_math_utils.py"

# ── Parche 1: guard fail-loud en la firma/inicio de la función ───────────
# Anchor = firma completa + primera línea del cuerpo, tal como aparece en
# el grep (líneas 219-227). Único en el archivo por construcción (una sola
# función con ese nombre).

_GUARD_ANCHOR = '''def noisy_or_correlated(
    severities: List[Fraction],
    correlation_groups: Optional[Dict[int, Set[int]]] = None,
    penalty: Fraction = Fraction(15, 100),
    penalty_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
    if not severities:
        return Fraction(0, 1)'''

_GUARD_REPLACEMENT = '''def noisy_or_correlated(
    severities: List[Fraction],
    correlation_groups: Optional[Dict[int, Set[int]]] = None,
    penalty: Fraction = Fraction(15, 100),
    penalty_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
    if correlation_groups is not None and not isinstance(correlation_groups, dict):
        raise TypeError(
            f"noisy_or_correlated: correlation_groups must be "
            f"Dict[int, Set[int]] or None, got {type(correlation_groups).__name__}. "
            f"Use build_correlation_groups() to construct it. (B-047)"
        )
    if not severities:
        return Fraction(0, 1)'''

# ── Parche 2: helper canónico, insertado entre noisy_or_correlated y la
# siguiente función del archivo ────────────────────────────────────────────
# Anchor = las últimas líneas del cuerpo de noisy_or_correlated + las dos
# líneas en blanco + el inicio de apply_artifact_reliability, tal como
# aparece verbatim en el grep (líneas 242-249).

_HELPER_ANCHOR = '''    product = Fraction(1, 1)
    for sev in adjusted:
        product = product * (Fraction(1, 1) - sev)
    result = Fraction(1, 1) - product
    return min(result, Fraction(95, 100))


def apply_artifact_reliability('''

_HELPER_REPLACEMENT = '''    product = Fraction(1, 1)
    for sev in adjusted:
        product = product * (Fraction(1, 1) - sev)
    result = Fraction(1, 1) - product
    return min(result, Fraction(95, 100))


def build_correlation_groups(corr_tags: List[str]) -> Dict[int, Set[int]]:
    """Build the correlation map in the format noisy_or_correlated expects:
    Dict[int, Set[int]] where each finding index maps to the set of its
    correlated peers (same non-empty corr_group tag, self excluded).

    Only groups with >= 2 members produce entries. Findings with an empty
    corr_group tag are independent and never appear in the map.

    B-047 fix: single shared implementation replacing four per-module copies
    (macos_forensics, ios_forensics, android_forensics had List[List[int]] —
    a format noisy_or_correlated does not accept and previously crashed on
    with AttributeError as soon as a case produced >=2 correlated findings;
    google_takeout_forensics had this exact correct format).

    Args:
        corr_tags: corr_group tag of each finding, in finding order.
                   Index i in the returned map refers to corr_tags[i].
    """
    tag_groups: Dict[str, List[int]] = {}
    for i, tag in enumerate(corr_tags):
        if tag:
            tag_groups.setdefault(tag, []).append(i)
    result: Dict[int, Set[int]] = {}
    for indices in tag_groups.values():
        if len(indices) < 2:
            continue
        for idx in indices:
            peers = {j for j in indices if j != idx}
            if idx in result:
                result[idx] |= peers
            else:
                result[idx] = peers
    return result


def apply_artifact_reliability('''

PATCHES = [
    (_GUARD_ANCHOR, _GUARD_REPLACEMENT),
    (_HELPER_ANCHOR, _HELPER_REPLACEMENT),
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B-047: guard + helper en _math_utils.py (dry-run por defecto)."
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    dry = not args.apply

    if not Path(TARGET).is_file():
        sys.exit(f"[ERROR] No existe {TARGET} — ¿estás en la raíz del repo?")

    print(f"[B-047 core] Modo: {'DRY-RUN' if dry else 'APPLY'}")
    print(f"── {TARGET} (2 parches) " + "─" * 20)
    try:
        apply_surgical_patches(TARGET, PATCHES, dry_run=dry)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1

    if not dry:
        print(
            "\n[B-047 core] Aplicado. Los 3 params ya importados en el archivo "
            "(List, Dict, Set, Optional aparecen en la firma de "
            "noisy_or_correlated) — no debería requerir tocar imports. "
            "Verificar con:\n"
            "  python3 -c \"import ast; ast.parse(open('vigia/sift/_math_utils.py').read())\""
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
