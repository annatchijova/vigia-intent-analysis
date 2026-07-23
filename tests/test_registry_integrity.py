"""Contrato de integridad referencial de los registros L-*/B-*.

Cierra la clase de defecto detectada el 2026-07-23: el ID L-051 estaba
duplicado (dos limitaciones distintas, "Arbitration Contract" y "§9.4-LIM
ceiling", compartían número — segunda colisión de numeración del proyecto,
tras el precedente L-029/L-051 de 2026-07-08). Un registro legal-facing con
IDs ambiguos o referencias colgantes es un pasivo Daubert: la cita "ver
L-051" debe resolver a UNA entrada, siempre.

Dos garantías:
  1. SIN DUPLICADOS: dentro de cada archivo de registro, ningún ID L-/B-
     encabeza dos entradas distintas.
  2. SIN REFERENCIAS COLGANTES: todo ID L-/B- citado en superficies fuente
     (docs, código, tests) debe estar definido en el universo documentado.

Universo de definición (tres niveles, reflejo de la práctica real del repo):
  a. Headings h2-h4 de KNOWN_LIMITATIONS.md, BUGS_PENDIENTES.md,
     BUGS_PENDIENTES_EN.md y docs/*.md — tolera los formatos históricos
     `### [RESOLVED] L-019 — ...`, `### B-032 [FIXED] — ...` y los dossiers
     de auditoría que son registro canónico de bandas enteras (B-057..B-061
     viven en docs/AUDITORIA_INVARIANTES_ASIMETRIAS_20260703.md).
  b. Filas de índice "entry retired" (L-013 es un hueco documentado).
  c. Sub-IDs con letra (B-041a, L-037a): definidos si su padre tiene
     heading — la práctica del repo los define dentro del cuerpo del padre.

Los bundles históricos en results/ quedan FUERA del escaneo por diseño:
el precedente de numeración dice explícitamente que los artefactos sellados
conservan los números viejos.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REGISTRY_FILES = (
    "KNOWN_LIMITATIONS.md",
    "BUGS_PENDIENTES.md",
    "BUGS_PENDIENTES_EN.md",
)

_ID_RE = re.compile(r"\b([LB]-\d{3}[a-z]?)\b")
_HEADING_RE = re.compile(r"^#{2,4} (.*)$", re.M)
_RETIRED_ROW_RE = re.compile(r"^\|\s*([LB]-\d{3}[a-z]?)\s*\|\s*\*?\(gap — entry retired\)", re.M)

# Referencias históricas legítimas sin heading propio en ningún registro ni
# dossier. Cada entrada exige justificación — el test falla si la excepción
# queda huérfana de motivo.
ALLOWED_HISTORICAL: dict[str, str] = {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _defined_ids() -> set[str]:
    defined: set[str] = set()
    sources = [REPO / f for f in REGISTRY_FILES] + sorted((REPO / "docs").glob("*.md"))
    for src in sources:
        text = _read(src)
        for heading in _HEADING_RE.findall(text):
            defined.update(_ID_RE.findall(heading))
        defined.update(_RETIRED_ROW_RE.findall(text))
    return defined


def _reference_surfaces() -> list[Path]:
    surfaces: list[Path] = []
    surfaces += sorted(REPO.glob("*.md"))
    surfaces += sorted((REPO / "docs").glob("*.md"))
    surfaces += sorted(REPO.glob("*.py"))
    surfaces += sorted((REPO / "vigia").rglob("*.py"))
    surfaces += sorted((REPO / "tests").rglob("*.py"))
    surfaces += sorted((REPO / "scripts").glob("*.py"))
    return [
        p for p in surfaces
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


def test_no_duplicate_registry_ids() -> None:
    """Ningún ID puede encabezar dos entradas del mismo registro (clase L-051 dup)."""
    problems: list[str] = []
    for fname in REGISTRY_FILES:
        text = _read(REPO / fname)
        seen: dict[str, int] = defaultdict(int)
        for line_no, line in enumerate(text.splitlines(), 1):
            # Práctica del repo: los diagnósticos EQUIVOCADOS se preservan
            # como audit trail con el marcador [SUPERSEDIDO]/[SUPERSEDED]
            # apuntando a la entrada corregida (ej. el primer B-041). Ese
            # heading no es una segunda entrada — es historia.
            if "[SUPERSEDIDO" in line or "[SUPERSEDED" in line:
                continue
            m = re.match(r"^#{2,3} (?:\[[A-Z ]+\] )?([LB]-\d{3}[a-z]?)\b", line)
            if m:
                seen[m.group(1)] += 1
        dupes = {k: v for k, v in seen.items() if v > 1}
        if dupes:
            problems.append(f"{fname}: IDs duplicados en headings: {dupes}")
    assert not problems, (
        "IDs de registro duplicados — cada cita debe resolver a UNA entrada "
        f"(precedente L-029/L-051 y L-051/L-067): {problems}"
    )


def test_no_dangling_registry_references() -> None:
    """Todo L-*/B-* citado en fuentes debe existir en el universo documentado."""
    defined = _defined_ids()
    dangling: dict[str, set[str]] = defaultdict(set)
    for surface in _reference_surfaces():
        text = _read(surface)
        for rid in set(_ID_RE.findall(text)):
            if rid in defined or rid in ALLOWED_HISTORICAL:
                continue
            # Sub-ID con letra: definido si el padre tiene heading (práctica
            # del repo: los sub-bugs viven en el cuerpo de la entrada padre).
            if rid[-1].isalpha() and rid[:-1] in defined:
                continue
            dangling[rid].add(surface.name)
    assert not dangling, (
        "Referencias colgantes a IDs jamás definidos (agregar la entrada al "
        "registro, corregir la cita, o documentar la excepción en "
        f"ALLOWED_HISTORICAL con justificación): {dict(sorted(dangling.items()))}"
    )


def _b_heading_ids(fname: str) -> set[str]:
    ids: set[str] = set()
    for line in _read(REPO / fname).splitlines():
        if "[SUPERSEDIDO" in line or "[SUPERSEDED" in line:
            continue
        m = re.match(r"^#{2,3} (?:\[[A-Z ]+\] )?(B-\d{3}[a-z]?)\b", line)
        if m:
            ids.add(m.group(1))
    return ids


def test_es_en_registry_parity() -> None:
    """Ambos registros documentan el MISMO conjunto de bugs B-*.

    Sentinela promovida a guarda dura el 2026-07-23 (patrón B-097): el
    empalme EN de B-111..B-115 + REVIEW-001 aterrizó en esta sesión.

    Deriva detectada dos veces (2026-07-22: EN sin B-167..B-210;
    2026-07-23: EN sin B-111..B-115 y ES sin B-145..B-152). Un registro
    espejo que diverge en contenido deja de ser espejo: el lector de un
    idioma cree tener el cuadro completo y no lo tiene.
    """
    es = _b_heading_ids("BUGS_PENDIENTES.md")
    en = _b_heading_ids("BUGS_PENDIENTES_EN.md")
    only_es = sorted(es - en)
    only_en = sorted(en - es)
    assert not only_es and not only_en, (
        f"Registros desincronizados — solo en ES: {only_es}; "
        f"solo en EN: {only_en}. Traducir las entradas faltantes "
        "(no borrar las presentes)."
    )


def test_allowlist_entries_carry_justification() -> None:
    """La excepción sin motivo es peor que el hueco: cada entrada lo exige."""
    for rid, reason in ALLOWED_HISTORICAL.items():
        assert isinstance(reason, str) and len(reason) >= 20, (
            f"ALLOWED_HISTORICAL[{rid!r}] sin justificación sustantiva"
        )
