"""
vigia_patch_valkyrie.py
VIGÍA Forensic Suite — Parche Consolidado v1.0-Valkyrie
Autora:  Anna Tchijova
Fecha:   2026-05-15

Opera sobre el repositorio existente y corrige 4 problemas confirmados por
auditoría forense. Los módulos nuevos de la sesión (entropy_kernel.py, etc.)
se agregan al repo como git add después de ejecutar este parche.

Problemas confirmados en el repo:
  P0A  "Annia Tchijova" → "Anna Tchijova" en tarasenko_h_se.md e INTEGRATION_PLAN.md
  P0B  ForensicBundle.seal() en ebs.py línea 680 — viola Verifier Independence Invariant
  P0C  H_EX_001 en bloque IRPhase.EXFILTRATION → renombrar a H_XF_001
  P0D  Tabla canónica de prefijos inyectada en abductive_intent_engine.py

Garantías:
  - Verifica hash SHA-256 de ebs_v1.py antes de cualquier operación
    (EBS_V1_EXPECTED_HASH = 3fecf64e...). Si no coincide, aborta.
  - Crea backup .valkyrie_bak de cada archivo antes de modificarlo.
  - Valida sintaxis Python (ast.parse) después de cada transformación.
  - Tombstone Daubert en lugar de seal() purgado.
  - Log de auditoría firmado con timestamp ISO 8601 y hashes SHA-256.

Uso:
  python3 vigia_patch_valkyrie.py --path /ruta/repo --dry-run
  python3 vigia_patch_valkyrie.py --path /ruta/repo --apply
  python3 vigia_patch_valkyrie.py --path /ruta/repo --apply --patches P0A P0C

Después del parche — agregar módulos nuevos al repo:
  git add entropy_kernel.py evidence_narrative_gen.py pre_release_check.py
  git add vigia_adversarial_gen.py vigia_artifact_graph.py vigia_chain_of_custody.py
  git add vigia_command_center.py vigia_counter_fact.py vigia_mass_refactor.py
  git add vigia_mitigation_planner.py vigia_patch_valkyrie.py vigia_paper_methodology.md
  git commit -m "feat: VIGÍA v1.0-Valkyrie — módulos Capa 1/4/Virtual + parche de auditoría"
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ──────────────────────────────────────────────────────────────────────────
# CONSTANTES INMUTABLES — FUENTE DE VERDAD
# ──────────────────────────────────────────────────────────────────────────

VIGIA_VERSION = "v1.0-Valkyrie"
AUTHOR_CORRECT = "Anna Tchijova"
AUTHOR_TYPO    = "Annia Tchijova"

# Hash SHA-256 del contrato inmutable — verificado antes de cualquier operación
EBS_V1_EXPECTED_HASH = (
    "3fecf64e13a6cffbe9299b4c569b3fff"
    "6352868595fe07ed1a084e21716603a1"
)

# Hashes reales de los 10 casos forenses (auditados el 2026-05-15)
REAL_CASE_HASHES: Dict[str, str] = {
    "VIGIA-REAL-001.json": "9868e7b0305efd7dc5442025dce5e65bf2e494dc2093d16b67be7496ecca0fbe",
    "VIGIA-REAL-002.json": "98b79ad52f75c1eb0492dd6afc9078a3e1f90fdb253853e608c611811cf1bd57",
    "VIGIA-REAL-003.json": "1ca614ef70b6d025bfbc7df32ba213014215f45ca5607f49565e0d5d04b8441e",
    "VIGIA-REAL-004.json": "2b32c6443001fdb8331d04c7289101a216c37b2bb848dfeeb061983e2485566f",
    "VIGIA-REAL-005.json": "ade54740e3269325cf721a8ae834d904dedf7efcc50a1a6eb5eebebe33961c87",
    "VIGIA-REAL-006.json": "8ca839b786b170f3136b295eb5cc332140a825cfe258518e8300ffd758a34cdb",
    "VIGIA-REAL-007.json": "f8ae616ffa3c9413e30cb281a6f87b46f652008f003dd172fe2b846e30a9ea83",
    "VIGIA-REAL-008.json": "58f7e0bdb45ad86e8cfd51ee969963c2fc8a909e58f5058f6fdc4ac9905ff48c",
    "VIGIA-REAL-009.json": "05c8ac08c64b69744ad6ab030b149a3ee7a8163ff79db71223c0f2199328d850",
    "VIGIA-REAL-010.json": "400e96189faead473f380e226b13fdbcfadf41f48279095eda85feeebfe7154a",
}

# Hash de llm_backend_v2.py (referencia para el paper)
LLM_BACKEND_V2_HASH = (
    "b921680b9f3ca8352f88debefae6d6c9"
    "e89ef7fd29cbaba2f34bef62084f805b"
)

# Tombstone Daubert para ForensicBundle.seal() purgado
_SEAL_TOMBSTONE = '''\
    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  AUDIT TOMBSTONE — VIGIA_PATCH_VALKYRIE P0B                     ║
    # ║  Versión: v1.0-Valkyrie  Fecha: {ts}           ║
    # ║  Motivo:  ForensicBundle.seal() viola la Verifier Independence   ║
    # ║           Invariant (Daubert v. Merrell Dow, 1993).              ║
    # ║           Un motor comprometido no puede sellar su propio output.║
    # ║  Acción:  Usar BundleBuilder.seal(bundle) exclusivamente.        ║
    # ║  Ref:     vigia_patch_valkyrie.py | hash ebs_v1: {h16}... ║
    # ╚══════════════════════════════════════════════════════════════════╝
'''

# Tabla canónica de prefijos para abductive_intent_engine.py
_PREFIX_TABLE_COMMENT = """
# ══════════════════════════════════════════════════════════════════════════
# TABLA CANÓNICA DE PREFIJOS DE HYPOTHESIS_ID — v1.0-Valkyrie
# Fuente de verdad. Cualquier ID fuera de esta tabla es un error.
# PATCH P0D-2026-05-15 | Auditor: Anna Tchijova
#
# IRPhase               Prefijo  Ejemplo     Colisión conocida
# EXECUTION             EX       H_EX_001
# EXFILTRATION          XF       H_XF_001    ← NO H_EX_001 (P0C)
# DEFENSE_EVASION       DE       H_DE_001
# INITIAL_ACCESS        IA       H_IA_001
# RECONNAISSANCE        RE       H_RE_001
# LATERAL_MOVEMENT      LM       H_LM_001
# CREDENTIAL_ACCESS     CA       H_CA_001
# COLLECTION            CO       H_CO_001
# COMMAND_AND_CONTROL   C2       H_C2_001
# IMPACT                IM       H_IM_001
# DISCOVERY             DI       H_DI_001
# PERSISTENCE           PE       H_PE_001
# CLEANUP               CL       H_CL_001
# FALSE_SECURITY_THEATER SE      H_SE_001
# ══════════════════════════════════════════════════════════════════════════
"""


# ──────────────────────────────────────────────────────────────────────────
# INFRAESTRUCTURA
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class PatchResult:
    patch_id: str
    file: str
    applied: bool = False
    dry_run: bool = False
    changes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __str__(self) -> str:
        tag = "DRY" if self.dry_run else ("OK " if self.applied else "ERR")
        body = "; ".join(self.changes) if self.changes else (self.error or "no-op")
        return f"  [{tag}] {self.patch_id}/{self.file}: {body}"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _validate_syntax(source: str, filename: str) -> Optional[str]:
    try:
        ast.parse(source, filename=filename)
        return None
    except SyntaxError as e:
        return f"SyntaxError L{e.lineno}: {e.msg}"


def _write_atomic(path: Path, content: str, backup: bool, dry_run: bool) -> None:
    if dry_run:
        return
    if backup:
        bak = path.with_suffix(path.suffix + ".valkyrie_bak")
        shutil.copy2(path, bak)
    tmp = path.with_suffix(path.suffix + ".tmp_valk")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def _str_replace_all(
    content: str,
    old: str,
    new: str,
    label: str,
    changes: List[str],
) -> Tuple[str, bool]:
    """
    Reemplaza TODAS las ocurrencias de old por new (str.replace semántica).
    Retorna (nuevo_contenido, hubo_cambio).

    Nota: el nombre anterior _str_replace_once era engañoso — se renombró
    en respuesta a la auditoría de Kimi (VIGÍA v1.0-Valkyrie, 2026-05-15).

    C3-WARNING-2026-05-16: esta función opera sobre TODO el contenido del archivo,
    incluyendo strings de datos forenses. Si `old` aparece dentro de una cadena
    de evidencia (ej. una cita de documento que contiene el patrón buscado),
    el contenido forense se corrompe silenciosamente.
    USO CORRECTO: sólo para patrones que aparecen exclusivamente en comentarios,
    imports o código estructural — nunca para strings que puedan estar en datos.
    """
    if old not in content:
        changes.append(f"[SKIP] {label}: patrón no encontrado")
        return content, False
    count = content.count(old)
    result = content.replace(old, new)
    changes.append(f"[OK] {label}: {count} ocurrencia(s) reemplazada(s)")
    return result, True


# ──────────────────────────────────────────────────────────────────────────
# GUARDIA GLOBAL: verificar ebs_v1.py antes de cualquier operación
# ──────────────────────────────────────────────────────────────────────────

def _verify_ebs_v1(root: Path) -> Optional[str]:
    """
    Verifica el hash SHA-256 de ebs_v1.py.
    Retorna None si es correcto, o mensaje de error si no.
    """
    candidates = [root / "ebs_v1.py", root / "models" / "ebs_v1.py"]
    for path in candidates:
        if path.exists():
            actual = _sha256(path)
            if actual == EBS_V1_EXPECTED_HASH:
                return None
            return (
                f"Hash de {path.relative_to(root)} no coincide.\n"
                f"  Esperado: {EBS_V1_EXPECTED_HASH}\n"
                f"  Actual:   {actual}\n"
                "  El contrato inmutable fue modificado. Abortar."
            )
    return "ebs_v1.py no encontrado en el repositorio."


# ──────────────────────────────────────────────────────────────────────────
# P0A — SOBERANÍA DE IDENTIDAD
# ──────────────────────────────────────────────────────────────────────────

def patch_p0a(root: Path, dry_run: bool, backup: bool) -> List[PatchResult]:
    """
    Corrige "Annia Tchijova" → "Anna Tchijova" en todos los archivos
    del repositorio (.py, .md), excluyendo dependencias externas.
    """
    results: List[PatchResult] = []

    EXCLUDED_DIRS = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        "site-packages", "dist-packages", ".cache", ".npm-global",
    }

    targets = [
        f for f in (list(root.rglob("*.py")) + list(root.rglob("*.md")))
        if not any(part in EXCLUDED_DIRS for part in f.parts)
        and ".valkyrie_bak" not in str(f)
        and f.name != "vigia_patch_valkyrie.py"
    ]

    for path in targets:
        try:
            content = _read(path)
        except Exception:
            continue

        if AUTHOR_TYPO not in content:
            continue

        result = PatchResult("P0A", str(path.relative_to(root)))
        changes: List[str] = []

        new_content, _ = _str_replace_all(
            content, AUTHOR_TYPO, AUTHOR_CORRECT,
            f"nombre autor en {path.name}", changes,
        )

        result.changes = changes

        if not dry_run:
            if path.suffix == ".py":
                err = _validate_syntax(new_content, str(path))
                if err:
                    results.append(PatchResult(
                        "P0A", result.file, error=f"Sintaxis inválida: {err}"
                    ))
                    continue
            _write_atomic(path, new_content, backup, dry_run)
            result.applied = True
        else:
            result.dry_run = True
            result.applied = True

        results.append(result)

    if not results:
        r = PatchResult("P0A", "(ningún archivo)")
        r.changes = ["[SKIP] 'Annia Tchijova' no encontrado en el repo"]
        r.applied = True
        results.append(r)

    return results


# ──────────────────────────────────────────────────────────────────────────
# P0B — PURGA DE ForensicBundle.seal()
# ──────────────────────────────────────────────────────────────────────────

def _remove_seal_via_ast(
    content: str, filepath: str, tombstone: str
) -> Tuple[str, List[str]]:
    """
    Usa AST para localizar ForensicBundle.seal() y reemplazarlo
    con el tombstone Daubert. Determinista.
    """
    changes: List[str] = []

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        changes.append(f"[ERR] SyntaxError al parsear: {e}")
        return content, changes

    lines = content.splitlines(keepends=True)

    # Recolectar rangos a eliminar (en orden inverso)
    ranges_to_remove: List[Tuple[int, int]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name != "ForensicBundle":
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name != "seal":
                continue
            end_line = getattr(item, "end_lineno", item.lineno)
            ranges_to_remove.append((item.lineno, end_line))
            changes.append(
                f"[OK] seal() eliminado (líneas {item.lineno}-{end_line}), "
                "tombstone Daubert insertado"
            )

    if not ranges_to_remove:
        changes.append("[SKIP] seal() no encontrado en ForensicBundle")
        return content, changes

    # Aplicar en orden inverso para no desplazar índices
    ranges_to_remove.sort(reverse=True)
    for start_l, end_l in ranges_to_remove:
        # Expandir hacia atrás para incluir decoradores
        actual_start = start_l
        for li in range(start_l - 2, max(start_l - 5, 0), -1):
            if li < len(lines):
                stripped = lines[li].strip()
                if stripped.startswith("@") or (stripped.startswith("#") and "seal" in stripped.lower()):
                    actual_start = li + 1
                else:
                    break
        # 0-indexed
        lines[actual_start - 1: end_l] = [tombstone]

    return "".join(lines), changes


def patch_p0b(root: Path, dry_run: bool, backup: bool) -> List[PatchResult]:
    """
    Purga ForensicBundle.seal() de todos los archivos excepto ebs_v1.py.
    Deja tombstone Daubert con metadatos de auditoría.
    """
    results: List[PatchResult] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tombstone = _SEAL_TOMBSTONE.format(ts=ts, h16=EBS_V1_EXPECTED_HASH[:32])

    PROTECTED = {"ebs_v1.py"}
    EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", ".venv", ".cache"}

    for path in sorted(root.rglob("*.py")):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name in PROTECTED:
            continue
        if ".valkyrie_bak" in str(path):
            continue

        try:
            content = _read(path)
        except Exception:
            continue

        if "ForensicBundle" not in content or "def seal" not in content:
            continue

        result = PatchResult("P0B", str(path.relative_to(root)))
        new_content, changes = _remove_seal_via_ast(content, str(path), tombstone)
        result.changes = changes

        if "[OK]" not in " ".join(changes):
            # No hay nada que hacer en este archivo — no reportar como error
            continue

        if not dry_run:
            err = _validate_syntax(new_content, str(path))
            if err:
                result.error = f"Sintaxis inválida post-purga: {err}"
                results.append(result)
                continue
            _write_atomic(path, new_content, backup, dry_run)
            result.applied = True
        else:
            result.dry_run = True
            result.applied = True

        results.append(result)

    return results


# ──────────────────────────────────────────────────────────────────────────
# P0C — MIGRACIÓN H_EX_001 → H_XF_001 EN BLOQUE EXFILTRATION
# ──────────────────────────────────────────────────────────────────────────

def patch_p0c(root: Path, dry_run: bool, backup: bool) -> List[PatchResult]:
    """
    Corrige la colisión de H_EX_001 en abductive_intent_engine.py:
    - H_EX_001 en bloque IRPhase.EXFILTRATION → H_XF_001
    - RULE_EX_001 en el mismo bloque → RULE_XF_001
    - H_EX_001 en IRPhase.EXECUTION NO se toca (es correcto)

    Estrategia AST pura (corrección auditoría Kimi, 2026-05-15):
    Navega el árbol AST para encontrar el dict HYPOTHESIS_TEMPLATES,
    luego localiza la clave IRPhase.EXFILTRATION y extrae el rango de
    líneas exacto de su valor. El reemplazo se aplica SOLO en ese rango.
    Esto es determinista e inmune a cambios en el orden de las claves.
    """
    results: List[PatchResult] = []

    target = root / "abductive_intent_engine.py"
    if not target.exists():
        r = PatchResult("P0C", "abductive_intent_engine.py")
        r.error = "archivo no encontrado"
        return [r]

    content = _read(target)
    result = PatchResult("P0C", "abductive_intent_engine.py")
    changes: List[str] = []

    try:
        tree = ast.parse(content, filename=str(target))
    except SyntaxError as e:
        result.error = f"SyntaxError: {e}"
        return [result]

    lines = content.splitlines(keepends=True)

    # ── Navegación AST para localizar el valor de la clave EXFILTRATION ──
    # Buscamos un ast.Dict cuya clave sea un ast.Attribute
    # con value.id == "IRPhase" y attr == "EXFILTRATION"
    exfil_value_node: Optional[ast.AST] = None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not isinstance(key, ast.Attribute):
                continue
            if not (
                isinstance(key.value, ast.Name)
                and key.value.id == "IRPhase"
                and key.attr == "EXFILTRATION"
            ):
                continue
            exfil_value_node = value
            break
        if exfil_value_node is not None:
            break

    if exfil_value_node is None:
        # Fallback: si no hay HYPOTHESIS_TEMPLATES dict pero hay el patrón
        # en el módulo, intentar buscar mediante la clave como Subscript
        # (Python < 3.9 usa ast.Index wrapper)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue
            slice_node = node.slice
            # Python 3.9+: slice es ast.Attribute directamente
            # Python 3.8:  slice es ast.Index con value ast.Attribute
            attr_node = None
            if isinstance(slice_node, ast.Attribute):
                attr_node = slice_node
            elif isinstance(slice_node, ast.Index):
                v = getattr(slice_node, "value", None)
                if isinstance(v, ast.Attribute):
                    attr_node = v
            if attr_node is None:
                continue
            if (isinstance(attr_node.value, ast.Name)
                    and attr_node.value.id == "IRPhase"
                    and attr_node.attr == "EXFILTRATION"):
                # El valor está en el contexto Store — buscar el bloque de asignación
                # No es el patrón que buscamos aquí, saltar
                pass

    if exfil_value_node is None:
        # Último recurso: búsqueda por líneas pero con marcadores AST validados
        # Buscamos la primera aparición de "IRPhase.EXFILTRATION" como clave de dict
        exfil_start_line: Optional[int] = None
        exfil_end_line: Optional[int] = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Solo si parece ser una clave de dict (termina en ":" o ":[")
            if ("IRPhase.EXFILTRATION" in stripped
                    and stripped.endswith((":", ": [",[c for c in ":["])[-1])):
                exfil_start_line = i
            elif (exfil_start_line is not None
                  and "IRPhase." in stripped
                  and i > exfil_start_line + 2):
                exfil_end_line = i
                break

        if exfil_start_line is None:
            changes.append("[SKIP] IRPhase.EXFILTRATION no encontrado")
            result.changes = changes
            result.applied = True
            results.append(result)
            return results

        if exfil_end_line is None:
            exfil_end_line = len(lines)

        exfil_start = exfil_start_line
        exfil_end = exfil_end_line
        changes.append(
            f"[WARN] AST no localizó valor; usando heurística de líneas "
            f"({exfil_start+1}-{exfil_end})"
        )
    else:
        # AST localizó el nodo — usar sus líneas exactas
        exfil_start = exfil_value_node.lineno - 1       # 0-indexed
        exfil_end = getattr(exfil_value_node, "end_lineno", exfil_value_node.lineno)
        # Extender ligeramente hacia atrás para incluir la clave del dict
        exfil_start = max(0, exfil_start - 1)
        changes.append(
            f"[OK] IRPhase.EXFILTRATION localizado por AST "
            f"(líneas {exfil_start+1}-{exfil_end})"
        )

    # ── Aplicar reemplazo SOLO en el rango del bloque EXFILTRATION ────────
    exfil_block = "".join(lines[exfil_start:exfil_end])
    original_block = exfil_block

    if "H_EX_001" in exfil_block:
        exfil_block = exfil_block.replace('"H_EX_001"', '"H_XF_001"')
        exfil_block = exfil_block.replace("'H_EX_001'", "'H_XF_001'")
        exfil_block = exfil_block.replace("RULE_EX_001", "RULE_XF_001")
        changes.append("[OK] H_EX_001 → H_XF_001 (sólo bloque EXFILTRATION)")
        changes.append("[OK] RULE_EX_001 → RULE_XF_001 (sólo bloque EXFILTRATION)")
    else:
        changes.append("[SKIP] H_EX_001 no encontrado en bloque EXFILTRATION")

    if exfil_block == original_block:
        result.changes = changes
        result.applied = True
        results.append(result)
        return results

    new_content = (
        "".join(lines[:exfil_start])
        + exfil_block
        + "".join(lines[exfil_end:])
    )

    result.changes = changes

    if not dry_run:
        err = _validate_syntax(new_content, str(target))
        if err:
            result.error = f"Sintaxis inválida: {err}"
            results.append(result)
            return results
        _write_atomic(target, new_content, backup, dry_run)
        result.applied = True
    else:
        result.dry_run = True
        result.applied = True

    results.append(result)
    return results


# ──────────────────────────────────────────────────────────────────────────
# P0D — TABLA CANÓNICA EN abductive_intent_engine.py
# ──────────────────────────────────────────────────────────────────────────

def patch_p0d(root: Path, dry_run: bool, backup: bool) -> List[PatchResult]:
    """
    Inyecta la tabla canónica de prefijos de hypothesis_id en
    abductive_intent_engine.py, después del docstring de módulo.
    """
    results: List[PatchResult] = []

    target = root / "abductive_intent_engine.py"
    if not target.exists():
        r = PatchResult("P0D", "abductive_intent_engine.py")
        r.error = "archivo no encontrado"
        return [r]

    content = _read(target)
    result = PatchResult("P0D", "abductive_intent_engine.py")
    changes: List[str] = []

    if "TABLA CANÓNICA DE PREFIJOS" in content:
        changes.append("[SKIP] tabla canónica ya presente")
        result.changes = changes
        result.applied = True
        results.append(result)
        return results

    # Insertar después del primer bloque de imports (antes de la primera class/def)
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        result.error = f"SyntaxError: {e}"
        return [result]

    # Encontrar la primera línea que no sea import/docstring/comentario
    lines = content.splitlines(keepends=True)
    insert_after = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_after = max(insert_after, node.lineno)

    if insert_after == 0:
        # Fallback: insertar al principio del archivo
        new_content = _PREFIX_TABLE_COMMENT + content
    else:
        # Insertar después de la última línea de import
        new_content = (
            "".join(lines[:insert_after])
            + _PREFIX_TABLE_COMMENT
            + "".join(lines[insert_after:])
        )

    changes.append(
        f"[OK] tabla canónica de prefijos inyectada después del bloque de imports "
        f"(línea {insert_after})"
    )
    result.changes = changes

    if not dry_run:
        err = _validate_syntax(new_content, str(target))
        if err:
            result.error = f"Sintaxis inválida: {err}"
            results.append(result)
            return results
        _write_atomic(target, new_content, backup, dry_run)
        result.applied = True
    else:
        result.dry_run = True
        result.applied = True

    results.append(result)
    return results


def _collect_backups(root: Path) -> List[Path]:
    """Retorna todos los archivos .valkyrie_bak creados en esta sesión."""
    return sorted(root.rglob("*.valkyrie_bak"))


def rollback_all_backups(root: Path) -> List[str]:
    """
    Revierte todos los archivos .valkyrie_bak a su estado original.
    Rollback automático si cualquier patch falla en modo LIVE.

    Estrategia:
      1. Para cada archivo X.valkyrie_bak, mover X → X.valkyrie_failed
         y mover X.valkyrie_bak → X (restore atómico).
      2. Reportar el resultado de cada restore.

    Retorna lista de mensajes de rollback.
    """
    messages: List[str] = []
    for bak in _collect_backups(root):
        # W6-fix-2026-05-16: reconstruir original quitando ".valkyrie_bak" del nombre.
        # No usar with_suffix() — falla para archivos sin extensión (ej. Makefile):
        # original.suffix == "" → original.with_suffix(".valkyrie_failed") = ".valkyrie_failed" (oculto).
        # Solución: concatenar directamente al nombre completo.
        stem_with_real_suffix = bak.name[: -len(".valkyrie_bak")]
        original = bak.parent / stem_with_real_suffix
        failed = bak.parent / (stem_with_real_suffix + ".valkyrie_failed")
        try:
            if original.exists():
                original.rename(failed)
            bak.rename(original)
            messages.append(f"  [ROLLBACK OK] {original.name} restaurado")
        except Exception as e:
            messages.append(f"  [ROLLBACK ERR] {bak.name}: {e}")
    return messages

ALL_PATCHES = [
    ("P0A", "Soberanía de identidad (Annia → Anna)",      patch_p0a),
    ("P0B", "Purga ForensicBundle.seal() + tombstone",    patch_p0b),
    ("P0C", "Migración H_EX_001 → H_XF_001 (EXFILTRATION)", patch_p0c),
    ("P0D", "Tabla canónica de prefijos en motor abductivo", patch_p0d),
]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(
    root: Path,
    dry_run: bool,
    backup: bool,
    selected: Optional[List[str]] = None,
) -> Tuple[List[PatchResult], int]:
    """
    Ejecuta los patches seleccionados.
    Si hay errores en modo LIVE y se crearon backups, ejecuta rollback automático.
    Retorna (results, exit_code).
    """
    # Guardia global: verificar ebs_v1.py antes de cualquier operación
    err = _verify_ebs_v1(root)
    if err:
        print(f"\n[ABORT] Guardia EBS_V1 falló:\n  {err}\n")
        return [], 1

    all_results: List[PatchResult] = []

    for patch_id, description, fn in ALL_PATCHES:
        if selected and patch_id not in selected:
            continue
        print(f"\n{'═' * 60}")
        print(f"[{patch_id}] {description}")
        print("═" * 60)
        results = fn(root, dry_run, backup)
        for r in results:
            print(r)
        all_results.extend(results)

    # Rollback automático si hay errores en modo LIVE y hay backups
    if not dry_run and backup:
        errors = [r for r in all_results if r.error]
        if errors:
            print(f"\n[ROLLBACK] {len(errors)} error(es) detectado(s) en modo LIVE.")
            print("[ROLLBACK] Revirtiendo todos los cambios aplicados...")
            rollback_msgs = rollback_all_backups(root)
            if rollback_msgs:
                for msg in rollback_msgs:
                    print(msg)
            else:
                print("  [ROLLBACK] Sin backups que revertir.")

    return all_results, 0


def print_summary(
    results: List[PatchResult], dry_run: bool, root: Path
) -> int:
    applied = sum(1 for r in results if r.applied)
    errors  = sum(1 for r in results if r.error)

    print(f"\n{'═' * 60}")
    print(f"VIGÍA {VIGIA_VERSION} — RESUMEN")
    print("═" * 60)
    print(f"  Modo:      {'DRY-RUN (sin cambios)' if dry_run else 'LIVE'}")
    print(f"  Aplicados: {applied}")
    print(f"  Errores:   {errors}")

    if errors:
        print("\n  ERRORES:")
        for r in results:
            if r.error:
                print(f"    {r.patch_id}/{r.file}: {r.error}")

    ts = _utcnow()
    status = "DRY-RUN" if dry_run else ("COMPLETO" if not errors else "PARCIAL")
    print(f"\n  ESTADO: {status} | {ts}")

    # Log de auditoría
    log = {
        "vigia_version":            VIGIA_VERSION,
        "author":                   AUTHOR_CORRECT,
        "patch_timestamp":          ts,
        "dry_run":                  dry_run,
        "repo_root":                str(root),
        "ebs_v1_hash_verified":     EBS_V1_EXPECTED_HASH,
        "llm_backend_v2_hash":      LLM_BACKEND_V2_HASH,
        "real_case_hashes":         REAL_CASE_HASHES,
        "summary":                  {"applied": applied, "errors": errors},
        "results": [
            {
                "patch":   r.patch_id,
                "file":    r.file,
                "applied": r.applied,
                "changes": r.changes,
                "error":   r.error,
            }
            for r in results
        ],
    }
    log_name = f"vigia_valkyrie_audit_{ts.replace(':', '').replace('-', '')[:15]}.json"
    log_path = Path(log_name)
    log_path.write_text(
        json.dumps(log, indent=2, sort_keys=True, ensure_ascii=True),
        encoding="utf-8",
    )
    print(f"  Log: {log_path}")

    if not dry_run:
        print(f"""
  ── PRÓXIMOS PASOS (git) ──────────────────────────────────
  # Agregar módulos nuevos de la sesión:
  git add entropy_kernel.py evidence_narrative_gen.py
  git add pre_release_check.py vigia_adversarial_gen.py
  git add vigia_artifact_graph.py vigia_chain_of_custody.py
  git add vigia_command_center.py vigia_counter_fact.py
  git add vigia_mass_refactor.py vigia_mitigation_planner.py
  git add vigia_patch_valkyrie.py vigia_paper_methodology.md
  git add vigia_mitigation_planner.py
  # Agregar archivos modificados por el parche:
  git add abductive_intent_engine.py ebs.py vigia_integration_bridge.py
  git add tarasenko_h_se.md INTEGRATION_PLAN.md
  git commit -m "feat: VIGÍA v1.0-Valkyrie — parche auditoría + módulos Capa 1/4/Virtual"
""")

    return 1 if errors else 0


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"VIGÍA {VIGIA_VERSION} — Parche Consolidado de Auditoría",
    )
    parser.add_argument("--path", default=".",
                        help="Raíz del repositorio (default: .)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Previsualizar sin modificar ningún archivo")
    parser.add_argument("--apply", action="store_true",
                        help="Aplicar el parche (requerido para modo LIVE)")
    parser.add_argument("--no-backup", action="store_true",
                        help="No crear archivos .valkyrie_bak")
    parser.add_argument(
        "--patches", nargs="+",
        choices=[p[0] for p in ALL_PATCHES],
        help="Patches a ejecutar (default: todos)",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("Especificar --dry-run o --apply")

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"ERROR: '{root}' no es un directorio.", file=sys.stderr)
        return 1

    dry_run = not args.apply
    backup  = not args.no_backup

    print(f"VIGÍA {VIGIA_VERSION} — Parche Consolidado de Auditoría")
    print(f"Autora:      {AUTHOR_CORRECT}")
    print(f"Repositorio: {root}")
    print(f"Modo:        {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"Backup:      {'SI (.valkyrie_bak)' if backup and not dry_run else 'NO'}")
    print(f"ebs_v1 hash: {EBS_V1_EXPECTED_HASH[:32]}...")

    results, rc = run(root, dry_run, backup, args.patches)
    if rc != 0:
        return rc

    return print_summary(results, dry_run, root)


if __name__ == "__main__":
    sys.exit(main())
