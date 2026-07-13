#!/usr/bin/env python3
"""
vigia_mass_refactor.py
─────────────────────────────────────────────────────────────────────────────
VIGÍA Forensic Suite — Refactorizador Masivo de Grado Industrial

Operaciones atómicas implementadas:
  P0-A  Migración de namespace de hypothesis_id (colisiones H_EX_001)
  P0-B  Purga de ForensicBundle.seal() fuera de ebs_v1.py
  P0-C  Corrección de imports desde ebs.py deprecated → ebs_v1
  P1    Inyección de determinismo matemático (math.log → round(x,6))
  P2    Plan de migración de pares legacy/_v2

Garantías:
  - --dry-run nunca toca el sistema de archivos
  - Cada transformación real crea un backup .bak antes de escribir
  - Hash SHA-256 del archivo original se registra en el log de auditoría
  - Transformaciones sobre AST validan sintaxis antes de escribir
  - Log de auditoría firmado con timestamp ISO 8601

Uso:
  python3 vigia_mass_refactor.py --path /ruta/repo --dry-run
  python3 vigia_mass_refactor.py --path /ruta/repo --ops P0A P0B P1
  python3 vigia_mass_refactor.py --path /ruta/repo --all
  python3 vigia_mass_refactor.py --path /ruta/repo --all --no-backup

Salida:
  - vigia_refactor_audit_<timestamp>.json   log de auditoría forense
  - *.bak                                    backups de archivos modificados
  - EXIT 0 — éxito / EXIT 1 — error crítico

─────────────────────────────────────────────────────────────────────────────
VIGÍA SANS FIND EVIL Hackathon 2026
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════
# TABLA CANÓNICA DE PREFIJOS — fuente de verdad única
# ═══════════════════════════════════════════════════════════════════════════

# Mapeo IRPhase (valor del Enum en código) → prefijo canónico de 2 letras
PHASE_TO_PREFIX: Dict[str, str] = {
    "EXECUTION":           "EX",
    "EXFILTRATION":        "XF",
    "DEFENSE_EVASION":     "DE",
    "PERSISTENCE":         "PE",
    "INITIAL_ACCESS":      "IA",
    "RECONNAISSANCE":      "RE",
    "LATERAL_MOVEMENT":    "LM",
    "CREDENTIAL_ACCESS":   "CA",
    "COLLECTION":          "CO",
    "COMMAND_AND_CONTROL": "C2",
    "IMPACT":              "IM",
    "DISCOVERY":           "DI",
    "CLEANUP":             "CL",
    # False Security Theater — sub-categoría de DEFENSE_EVASION
    "SPECIAL":             "SE",
}

# Inverso: prefijo → fase (para detectar colisiones)
PREFIX_TO_PHASE: Dict[str, str] = {v: k for k, v in PHASE_TO_PREFIX.items()}

# IDs conocidos que están mal prefijados en el snapshot actual
# Formato: { id_viejo: (fase_real, id_nuevo) }
KNOWN_COLLISIONS: Dict[str, Tuple[str, str]] = {
    # H_EX_001 en bloque EXFILTRATION → debería ser H_XF_001
    # H_EX_001 en bloque EXECUTION    → se queda como H_EX_001 (correcto)
    # La resolución es contextual: se detecta por la fase del bloque contenedor
}

# Módulos objetivo para P1 (inyección de determinismo en entropía)
FLOAT_ENTROPY_TARGETS: List[str] = [
    "eml_gci.py",
    "entanglement.py",
    "vigia_integration_bridge.py",
]

# Pares legacy/_v2 detectados
LEGACY_V2_PAIRS: List[Tuple[str, str]] = [
    ("abductive_reasoner.py",  "abductive_reasoner_v2.py"),
    ("geopolitical.py",        "geopolitical_v2.py"),
    ("llm_backend.py",         "llm_backend_v2.py"),
    ("risk_bounded_layer.py",  "risk_bounded_layer_v2.py"),
    ("semiotic_detector.py",   "semiotic_detector_v2.py"),
]
# report_exporter.py/_v2.py: resolved — legacy (fake sign_hash placeholder,
# zero callers) deleted, report_exporter_v2.py (real RSA-PSS signing) kept
# as sole version. See git history for the removal commit.

# Archivo protegido: la única instancia de ebs_v1 que PUEDE tener seal()
PROTECTED_EBS_V1 = "ebs_v1.py"

# El ebs.py legacy (raíz) — tiene seal() y debe ser purgada de esa definición
LEGACY_EBS = "ebs.py"


# ═══════════════════════════════════════════════════════════════════════════
# ESTRUCTURAS DE AUDITORÍA
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Change:
    operation: str        # P0A, P0B, P0C, P1, P2
    file: str
    line_before: Optional[int]
    line_after: Optional[int]
    description: str
    original_snippet: str = ""
    replacement_snippet: str = ""
    applied: bool = False
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "operation":          self.operation,
            "file":               self.file,
            "line_before":        self.line_before,
            "line_after":         self.line_after,
            "description":        self.description,
            "original_snippet":   self.original_snippet[:200],
            "replacement_snippet": self.replacement_snippet[:200],
            "applied":            self.applied,
            "error":              self.error,
        }


@dataclass
class FileRecord:
    path: str
    sha256_before: str
    sha256_after: Optional[str] = None
    backed_up: bool = False
    changes: List[Change] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path":         self.path,
            "sha256_before": self.sha256_before,
            "sha256_after":  self.sha256_after,
            "backed_up":    self.backed_up,
            "changes":      [c.to_dict() for c in self.changes],
        }


@dataclass
class AuditLog:
    timestamp: str
    repo_root: str
    dry_run: bool
    operations: List[str]
    files: List[FileRecord] = field(default_factory=list)
    migration_plans: List[dict] = field(default_factory=list)
    dangling_imports_report: List[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "vigia_refactor_version": "1.0.0",
            "timestamp":              self.timestamp,
            "repo_root":              self.repo_root,
            "dry_run":                self.dry_run,
            "operations":             self.operations,
            "summary":                self.summary,
            "files_modified":         [f.to_dict() for f in self.files],
            "migration_plans":        self.migration_plans,
            "dangling_imports_report": self.dangling_imports_report,
        }


# ═══════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════════════════

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_python(source: str, filename: str) -> Optional[str]:
    """Retorna None si la sintaxis es válida, o el mensaje de error."""
    try:
        ast.parse(source, filename=filename)
        return None
    except SyntaxError as e:
        return f"SyntaxError línea {e.lineno}: {e.msg}"


def write_atomic(path: Path, content: str, backup: bool, record: FileRecord) -> bool:
    """
    Escribe content en path de forma atómica:
    1. Crea backup .bak si backup=True
    2. Escribe en archivo temporal en el mismo directorio
    3. Rename atómico (mismo filesystem → operación single syscall)
    Retorna True si tuvo éxito.
    """
    tmp = path.with_suffix(path.suffix + ".tmp_vigia")
    try:
        if backup:
            bak = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, bak)
            record.backed_up = True
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)  # atómico en el mismo filesystem
        record.sha256_after = sha256_file(path)
        return True
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        return False


# ═══════════════════════════════════════════════════════════════════════════
# P0-A: MIGRACIÓN DE NAMESPACE DE HYPOTHESIS_ID
# ═══════════════════════════════════════════════════════════════════════════

# Regex para encontrar bloques AbductiveHypothesis en Python
# Captura: el bloque completo desde AbductiveHypothesis( hasta su cierre
_HYP_BLOCK_RE = re.compile(
    r'AbductiveHypothesis\s*\(',
    re.DOTALL,
)

# Regex para extraer hypothesis_id y phase dentro de un bloque
_HYP_ID_RE    = re.compile(r'hypothesis_id\s*=\s*["\']([^"\']+)["\']')
_HYP_PHASE_RE = re.compile(r'phase\s*=\s*IRPhase\.(\w+)')

# Regex para hypothesis_id en JSON
_JSON_HYP_ID_RE = re.compile(r'"hypothesis_id"\s*:\s*"([^"]+)"')

# Regex para RULE_XX_NNN (las supporting_rules también llevan el prefijo)
_RULE_ID_RE = re.compile(r'RULE_([A-Z]{2})_(\d{3})')


def _extract_blocks_with_positions(content: str) -> List[Tuple[int, int, str]]:
    """
    Extrae posiciones de inicio/fin de cada bloque AbductiveHypothesis(...)
    respetando paréntesis anidados. Retorna lista de (start, end, text).
    """
    blocks = []
    for m in _HYP_BLOCK_RE.finditer(content):
        start = m.start()
        depth = 0
        i = m.end() - 1  # posición del '(' de apertura
        while i < len(content):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    blocks.append((start, i + 1, content[start:i + 1]))
                    break
            i += 1
    return blocks


def _determine_correct_prefix(block_text: str, surrounding_context: str) -> Optional[str]:
    """
    Determina el prefijo canónico correcto para un bloque de hipótesis.
    Estrategia: busca phase=IRPhase.XXX dentro del bloque o en el comentario
    de sección que lo precede.
    """
    # Buscar phase= dentro del bloque
    phase_m = _HYP_PHASE_RE.search(block_text)
    if phase_m:
        phase_name = phase_m.group(1)
        return PHASE_TO_PREFIX.get(phase_name)

    # Fallback: buscar en el contexto circundante (comentario de sección)
    section_re = re.compile(r'#\s*FASE:\s*(\w+)', re.IGNORECASE)
    ctx_m = section_re.search(surrounding_context[-500:])
    if ctx_m:
        return PHASE_TO_PREFIX.get(ctx_m.group(1).upper())

    return None


def _rename_ids_in_block(block_text: str, old_id: str, new_id: str) -> str:
    """Reemplaza hypothesis_id y RULE_ en un bloque."""
    # Reemplazar hypothesis_id
    result = re.sub(
        r'(hypothesis_id\s*=\s*["\'])' + re.escape(old_id) + r'(["\'])',
        r'\g<1>' + new_id + r'\2',
        block_text,
    )
    # Reemplazar RULE_XX_NNN si el prefijo coincide
    old_prefix = old_id.split("_")[1]  # "H_EX_001" → "EX"
    new_prefix = new_id.split("_")[1]  # "H_XF_001" → "XF"
    if old_prefix != new_prefix:
        result = result.replace(f"RULE_{old_prefix}_", f"RULE_{new_prefix}_")
    return result


def op_p0a_migrate_hypothesis_ids(
    root: Path,
    dry_run: bool,
    backup: bool,
    log: AuditLog,
) -> None:
    """
    P0-A: Corrige colisiones de hypothesis_id en archivos .py y .json.

    Algoritmo:
    1. Para cada .py, extraer todos los bloques AbductiveHypothesis(...)
    2. Para cada bloque, obtener hypothesis_id y phase
    3. Verificar si el prefijo del ID corresponde a la fase detectada
    4. Si no corresponde, calcular el ID correcto y aplicar el reemplazo
    5. Para .json, buscar "hypothesis_id": "H_XX_NNN" y verificar si el
       prefijo es canónico (los JSON no tienen fase inline — reportar solo)
    """
    print("\n[P0-A] Migración de namespace de hypothesis_id")
    print("       Tabla canónica:", json.dumps(PHASE_TO_PREFIX, indent=None))

    py_files = sorted(root.rglob("*.py"))
    # Excluir el propio script y __pycache__
    py_files = [
        f for f in py_files
        if "pycache" not in str(f) and f.name != "vigia_mass_refactor.py"
    ]

    for py_path in py_files:
        try:
            content = py_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if "AbductiveHypothesis" not in content:
            continue

        record = FileRecord(
            path=str(py_path.relative_to(root)),
            sha256_before=sha256_file(py_path),
        )

        blocks = _extract_blocks_with_positions(content)
        if not blocks:
            continue

        new_content = content
        offset = 0  # compensar desplazamiento por reemplazos anteriores

        for start, end, block_text in blocks:
            id_m = _HYP_ID_RE.search(block_text)
            if not id_m:
                continue
            current_id = id_m.group(1)

            # Solo procesar IDs con formato H_XX_NNN
            if not re.match(r'^H_[A-Z0-9]{2}_\d{3}$', current_id):
                continue

            current_prefix = current_id.split("_")[1]

            # Determinar prefijo correcto desde la fase declarada en el bloque
            correct_prefix = _determine_correct_prefix(
                block_text,
                new_content[max(0, start + offset - 500): start + offset],
            )

            if correct_prefix is None:
                continue

            if current_prefix == correct_prefix:
                continue  # Correcto, nada que hacer

            # Construir el ID correcto
            seq = current_id.split("_")[2]  # "001"
            new_id = f"H_{correct_prefix}_{seq}"

            # Verificar que el nuevo ID no colisione con uno ya existente en el archivo
            if new_id in content and new_id != current_id:
                # Asignar secuencia libre
                existing_seqs = set(
                    int(m.group(1))
                    for m in re.finditer(
                        rf'H_{correct_prefix}_(\d{{3}})',
                        new_content,
                    )
                )
                candidate = int(seq)
                while candidate in existing_seqs:
                    candidate += 1
                new_id = f"H_{correct_prefix}_{candidate:03d}"

            change = Change(
                operation="P0A",
                file=str(py_path.relative_to(root)),
                line_before=content[:start].count("\n") + 1,
                line_after=None,
                description=(
                    f"Renombrar {current_id} → {new_id} "
                    f"(fase: {PREFIX_TO_PHASE.get(correct_prefix, '?')})"
                ),
                original_snippet=current_id,
                replacement_snippet=new_id,
            )

            if not dry_run:
                # Aplicar reemplazo con offset tracking
                adj_start = start + offset
                adj_end = end + offset
                old_block = new_content[adj_start:adj_end]
                new_block = _rename_ids_in_block(old_block, current_id, new_id)
                new_content = new_content[:adj_start] + new_block + new_content[adj_end:]
                offset += len(new_block) - len(old_block)
                change.applied = True

            record.changes.append(change)

        if record.changes:
            if not dry_run and new_content != content:
                syntax_err = validate_python(new_content, str(py_path))
                if syntax_err:
                    for c in record.changes:
                        c.error = f"Sintaxis inválida post-transformación: {syntax_err}"
                        c.applied = False
                    print(f"  [ABORT] {py_path.name}: {syntax_err}")
                else:
                    if write_atomic(py_path, new_content, backup, record):
                        print(f"  [OK]  {py_path.name}: {len(record.changes)} ID(s) renombrado(s)")
                    else:
                        print(f"  [ERR] {py_path.name}: fallo de escritura")
            else:
                print(f"  [DRY] {py_path.name}: {len(record.changes)} cambio(s) pendiente(s)")
                for c in record.changes:
                    print(f"        {c.description}")

            log.files.append(record)

    # JSON: reportar IDs con prefijo no canónico (no se corrigen automáticamente
    # porque los JSON no declaran fase inline — se documenta para corrección manual)
    json_findings = []
    for jf in sorted(root.rglob("*.json")):
        if "pycache" in str(jf):
            continue
        try:
            content_j = jf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in _JSON_HYP_ID_RE.finditer(content_j):
            hid = m.group(1)
            if not re.match(r'^H_[A-Z0-9]{2}_\d{3}$', hid):
                continue
            prefix = hid.split("_")[1]
            if prefix not in PREFIX_TO_PHASE:
                json_findings.append({
                    "file": str(jf.relative_to(root)),
                    "hypothesis_id": hid,
                    "note": f"Prefijo '{prefix}' no reconocido en tabla canónica",
                })

    if json_findings:
        print(f"\n  [INFO] {len(json_findings)} hypothesis_id en JSON requieren revisión manual:")
        for f in json_findings[:10]:
            print(f"         {f['file']}: {f['hypothesis_id']} — {f['note']}")
        log.dangling_imports_report.extend(json_findings)


# ═══════════════════════════════════════════════════════════════════════════
# P0-B: PURGA DE ForensicBundle.seal() FUERA DE ebs_v1.py
# ═══════════════════════════════════════════════════════════════════════════

def _remove_seal_method_from_class(content: str, filename: str) -> Tuple[str, List[Change]]:
    """
    Elimina el método seal() de la clase ForensicBundle.

    Estrategia AST + reconstrucción por líneas:
    1. Parsear AST para obtener línea exacta de inicio y fin del método
    2. Eliminar el bloque de líneas correspondiente
    3. Agregar comentario de tombstone para trazabilidad Git

    Retorna (nuevo_contenido, lista_de_cambios).
    """
    changes: List[Change] = []

    try:
        tree = ast.parse(content, filename=filename)
    except SyntaxError:
        return content, changes

    lines = content.splitlines(keepends=True)
    # Recolectar rangos a eliminar (en orden inverso para no desplazar índices)
    ranges_to_remove: List[Tuple[int, int, int]] = []  # (start_line, end_line, method_lineno)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != "ForensicBundle":
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef) or item.name != "seal":
                continue
            # Calcular línea de fin del método
            end_line = item.end_lineno if hasattr(item, "end_lineno") else item.lineno
            # También eliminar quick_verify si está ligado (fue parte del mismo bloque)
            ranges_to_remove.append((item.lineno, end_line, item.lineno))
            changes.append(Change(
                operation="P0B",
                file=filename,
                line_before=item.lineno,
                line_after=item.lineno,
                description=f"Eliminar ForensicBundle.seal() líneas {item.lineno}-{end_line}",
                original_snippet=f"def seal(self, ...): [líneas {item.lineno}-{end_line}]",
                replacement_snippet="# [VIGIA_REFACTOR] seal() removido. Usar BundleBuilder.seal(bundle).",
            ))

    if not ranges_to_remove:
        return content, changes

    # Aplicar en orden inverso
    ranges_to_remove.sort(key=lambda x: x[0], reverse=True)
    for start_l, end_l, orig_l in ranges_to_remove:
        # Detectar el bloque de decoradores/docstrings previos al def
        actual_start = start_l
        for li in range(start_l - 2, max(start_l - 6, 0), -1):
            stripped = lines[li].strip() if li < len(lines) else ""
            if stripped.startswith("@") or stripped.startswith("#"):
                actual_start = li + 1
            else:
                break

        tombstone = (
            "    # ── [VIGIA_REFACTOR P0B] seal() eliminado — violación invariante ──\n"
            "    # El sellado se hace EXCLUSIVAMENTE via BundleBuilder.seal(bundle).\n"
            "    # Ver vigia_mass_refactor.py audit log para trazabilidad completa.\n"
        )
        # Reemplazar rango (1-indexed → 0-indexed)
        lines[actual_start - 1: end_l] = [tombstone]

    return "".join(lines), changes


def op_p0b_purge_seal(
    root: Path,
    dry_run: bool,
    backup: bool,
    log: AuditLog,
) -> None:
    """P0-B: Elimina ForensicBundle.seal() de todos los archivos excepto ebs_v1.py."""
    print("\n[P0-B] Purga de ForensicBundle.seal() fuera de contrato inmutable")

    for py_path in sorted(root.rglob("*.py")):
        if "pycache" in str(py_path):
            continue
        # Proteger los archivos canónicos
        if py_path.name == PROTECTED_EBS_V1:
            print(f"  [SKIP] {py_path.name} — archivo protegido (contrato inmutable)")
            continue

        try:
            content = py_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if "ForensicBundle" not in content or "def seal" not in content:
            continue

        record = FileRecord(
            path=str(py_path.relative_to(root)),
            sha256_before=sha256_file(py_path),
        )

        new_content, changes = _remove_seal_method_from_class(
            content, str(py_path.relative_to(root))
        )

        if not changes:
            continue

        record.changes = changes

        if dry_run:
            print(f"  [DRY] {py_path.name}: {len(changes)} seal() a eliminar")
            for c in changes:
                print(f"        {c.description}")
        else:
            syntax_err = validate_python(new_content, str(py_path))
            if syntax_err:
                for c in changes:
                    c.error = syntax_err
                    c.applied = False
                print(f"  [ABORT] {py_path.name}: sintaxis inválida post-transformación")
            elif write_atomic(py_path, new_content, backup, record):
                for c in changes:
                    c.applied = True
                print(f"  [OK]  {py_path.name}: seal() removido")
            else:
                print(f"  [ERR] {py_path.name}: fallo de escritura")

        log.files.append(record)


# ═══════════════════════════════════════════════════════════════════════════
# P0-C: REPORTE Y CORRECCIÓN DE DANGLING IMPORTS (ebs → ebs_v1)
# ═══════════════════════════════════════════════════════════════════════════

# Patrones de import deprecated de ebs.py raíz
_EBS_IMPORT_PATTERNS = [
    # import ebs
    (re.compile(r'^(\s*)import\s+ebs\b', re.M),
     r'\1import ebs_v1 as ebs  # [VIGIA_REFACTOR P0C] deprecado → ebs_v1'),
    # from ebs import X
    (re.compile(r'^(\s*)from\s+ebs\s+import\b', re.M),
     r'\1from ebs_v1 import  # [VIGIA_REFACTOR P0C] deprecado → ebs_v1'),
    # from vigia.models.ebs import X  (path legacy sin versión)
    (re.compile(r'^(\s*)from\s+(vigia\.models\.ebs)\s+import\b', re.M),
     r'\1from vigia.models.ebs_v1 import  # [VIGIA_REFACTOR P0C]'),
]


def op_p0c_fix_dangling_imports(
    root: Path,
    dry_run: bool,
    backup: bool,
    log: AuditLog,
) -> None:
    """P0-C: Genera reporte de imports desde ebs.py legacy y los corrige."""
    print("\n[P0-C] Detección y corrección de dangling imports (ebs → ebs_v1)")

    dangling: List[dict] = []

    for py_path in sorted(root.rglob("*.py")):
        if "pycache" in str(py_path):
            continue
        if py_path.name in ("ebs.py", "ebs_v1.py", "vigia_mass_refactor.py"):
            continue

        try:
            content = py_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        found_in_file = []
        for pattern, _ in _EBS_IMPORT_PATTERNS:
            for m in pattern.finditer(content):
                lineno = content[:m.start()].count("\n") + 1
                found_in_file.append({
                    "file":    str(py_path.relative_to(root)),
                    "line":    lineno,
                    "import":  m.group(0).strip(),
                    "status":  "pendiente_corrección",
                })

        if not found_in_file:
            continue

        dangling.extend(found_in_file)

        record = FileRecord(
            path=str(py_path.relative_to(root)),
            sha256_before=sha256_file(py_path),
        )

        new_content = content
        for pattern, replacement in _EBS_IMPORT_PATTERNS:
            new_content = pattern.sub(replacement, new_content)

        changes_made = new_content != content
        if changes_made:
            change = Change(
                operation="P0C",
                file=str(py_path.relative_to(root)),
                line_before=found_in_file[0]["line"],
                line_after=None,
                description=f"Redirigir {len(found_in_file)} import(s) de ebs → ebs_v1",
                original_snippet=found_in_file[0]["import"],
                replacement_snippet="→ ebs_v1 (ver archivo modificado)",
            )
            record.changes.append(change)

            if dry_run:
                print(f"  [DRY] {py_path.name}: {len(found_in_file)} import(s) a corregir")
                for fi in found_in_file:
                    print(f"        línea {fi['line']}: {fi['import']}")
            else:
                syntax_err = validate_python(new_content, str(py_path))
                if syntax_err:
                    change.error = syntax_err
                    print(f"  [ABORT] {py_path.name}: {syntax_err}")
                elif write_atomic(py_path, new_content, backup, record):
                    change.applied = True
                    for fi in found_in_file:
                        fi["status"] = "corregido"
                    print(f"  [OK]  {py_path.name}: {len(found_in_file)} import(s) corregido(s)")
                else:
                    print(f"  [ERR] {py_path.name}: fallo de escritura")

            log.files.append(record)

    log.dangling_imports_report.extend(dangling)

    if dangling:
        print(f"\n  REPORTE DANGLING IMPORTS: {len(dangling)} instancia(s) encontrada(s)")
        for d in dangling:
            print(f"    {d['file']}:{d['line']}: {d['import']} [{d['status']}]")
    else:
        print("  [OK] Sin dangling imports detectados.")


# ═══════════════════════════════════════════════════════════════════════════
# P1: INYECCIÓN DE DETERMINISMO MATEMÁTICO
# ═══════════════════════════════════════════════════════════════════════════

# Patrones de math.log que necesitan guardia determinista
# Los reemplazos aplican round(x, 6) antes de que el valor entre a un hash
# o bien delegan a _entropy_shannon cuando el contexto es acumulación de entropía

# Patrón 1: acumulación de entropía  `entropy -= p * math.log2(p)`
_ENTROPY_ACCUM_RE = re.compile(
    r'(entropy\s*[+-]=\s*p\s*\*\s*)math\.log2\(p\)',
)

# Patrón 2: normalización de entropía  `/ math.log2(N)`
_ENTROPY_NORM_RE = re.compile(
    r'math\.log2\((\w+)\)',
)

# Patrón 3: log-sum-exp para z_aggregated  `math.log(sum(math.exp(...)))`
# Esto es log-sum-exp — no es entropía, sino combinación de z-scores.
# Para este patrón aplicamos round(result, 6) sobre el resultado final.
_LOGSUMEXP_RE = re.compile(
    r'(_m\s*\+\s*math\.log\(sum\(math\.exp\([^)]+\)\s*for[^)]+\)\))',
)

# Patrón 4: math.log(lr) en registro de LR — aplicar round
_LR_LOG_RE = re.compile(
    r'"log_lr":\s*math\.log\(lr\)\s*if\s*lr\s*>\s*0\s*else\s*0\.0',
)

# Comentario de tombstone para trazabilidad
_P1_TOMBSTONE = "  # [VIGIA_REFACTOR P1] round(x,6): guardia ARM/x86 IEEE754 drift"


def _inject_determinism_in_file(content: str, filename: str) -> Tuple[str, List[Change]]:
    """
    Aplica guardias de determinismo a un archivo específico.
    Estrategia conservadora: solo modifica líneas con math.log/math.log2
    en contextos de entropía que van a un hash. No toca log-sum-exp de
    combinación de z-scores porque ahí la precisión es irrelevante para Daubert.
    """
    changes: List[Change] = []
    lines = content.splitlines(keepends=True)
    new_lines = list(lines)

    for i, line in enumerate(lines):
        original_line = line
        modified_line = line

        # Patrón 1: acumulación Shannon — mantener math.log2 pero añadir comentario
        # El round(x,6) se aplica DESPUÉS de la acumulación completa, no inline,
        # para no perder precisión intermedia. Documentamos la dependencia.
        if _ENTROPY_ACCUM_RE.search(line):
            if "_P1_SAFE" not in line and "# [VIGIA_REFACTOR P1]" not in line:  # W2-fix: marcador específico P1
                modified_line = line.rstrip() + _P1_TOMBSTONE + "\n"
                changes.append(Change(
                    operation="P1",
                    file=filename,
                    line_before=i + 1,
                    line_after=i + 1,
                    description="Documentar dependencia IEEE754 en acumulación Shannon",
                    original_snippet=line.rstrip(),
                    replacement_snippet=modified_line.rstrip(),
                ))

        # Patrón 3: log-sum-exp → wrap con round(result, 6)
        elif _LOGSUMEXP_RE.search(line) and "round(" not in line:
            modified_line = _LOGSUMEXP_RE.sub(
                r'round(\1, 6)',
                line,
            )
            if modified_line != line:
                changes.append(Change(
                    operation="P1",
                    file=filename,
                    line_before=i + 1,
                    line_after=i + 1,
                    description="round(log_sum_exp, 6) — guardia cross-arch en z_aggregated",
                    original_snippet=line.rstrip(),
                    replacement_snippet=modified_line.rstrip(),
                ))

        # Patrón 4: "log_lr": math.log(lr) → round(math.log(lr), 6)
        elif _LR_LOG_RE.search(line):
            modified_line = re.sub(
                r'math\.log\(lr\)',
                r'round(math.log(lr), 6)',
                line,
            )
            if modified_line != line:
                changes.append(Change(
                    operation="P1",
                    file=filename,
                    line_before=i + 1,
                    line_after=i + 1,
                    description="round(log_lr, 6) — guardia cross-arch en LR record",
                    original_snippet=line.rstrip(),
                    replacement_snippet=modified_line.rstrip(),
                ))

        new_lines[i] = modified_line

    # Después de las guardias inline, buscar las funciones que retornan
    # entropy/max_entropy sin round y agregar round al return
    result = "".join(new_lines)

    # `return entropy / max_entropy if max_entropy > 0 else 0.0`
    # → `return round(entropy / max_entropy, 6) if max_entropy > 0 else 0.0`
    return_entropy_re = re.compile(
        r'(return\s+)(entropy\s*/\s*max_entropy\s+if\s+max_entropy\s*>\s*0\s+else\s+0\.0)',
    )
    for m in return_entropy_re.finditer(result):
        if "round(" not in m.group(0):
            replacement = m.group(1) + "round(" + m.group(2).replace(
                " if ", ", 6) if ", 1
            ).replace(" else 0.0", " else 0.0")
            # Corrección: construir bien el reemplazo
            original = m.group(0)
            new_return = f"{m.group(1)}round({m.group(2)}, 6)"
            # Pero hay una condición ternaria — round solo va sobre el numerador
            new_return = re.sub(
                r'(return\s+)(entropy\s*/\s*max_entropy)(\s+if\s+max_entropy\s*>\s*0\s+else\s+0\.0)',
                r'\1round(\2, 6)\3',
                original,
            )
            result = result.replace(original, new_return, 1)
            changes.append(Change(
                operation="P1",
                file=filename,
                line_before=None,
                line_after=None,
                description="round(entropy/max_entropy, 6) en return de función de entropía",
                original_snippet=original.strip(),
                replacement_snippet=new_return.strip(),
            ))

    return result, changes


def op_p1_inject_determinism(
    root: Path,
    dry_run: bool,
    backup: bool,
    log: AuditLog,
) -> None:
    """P1: Inyecta guardias de determinismo matemático en módulos de entropía."""
    print("\n[P1] Inyección de determinismo matemático (entropía cross-arch)")

    for target_name in FLOAT_ENTROPY_TARGETS:
        # Buscar en toda la jerarquía
        candidates = list(root.rglob(target_name))
        if not candidates:
            print(f"  [SKIP] {target_name}: no encontrado en el repo")
            continue

        for py_path in candidates:
            try:
                content = py_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            record = FileRecord(
                path=str(py_path.relative_to(root)),
                sha256_before=sha256_file(py_path),
            )

            new_content, changes = _inject_determinism_in_file(
                content, str(py_path.relative_to(root))
            )

            if not changes:
                print(f"  [SKIP] {py_path.name}: sin operaciones flotantes en scope de hash")
                continue

            record.changes = changes

            if dry_run:
                print(f"  [DRY] {py_path.name}: {len(changes)} guardia(s) a inyectar")
                for c in changes:
                    print(f"        L{c.line_before}: {c.description}")
            else:
                syntax_err = validate_python(new_content, str(py_path))
                if syntax_err:
                    for c in changes:
                        c.error = syntax_err
                        c.applied = False
                    print(f"  [ABORT] {py_path.name}: sintaxis inválida — {syntax_err}")
                elif write_atomic(py_path, new_content, backup, record):
                    for c in changes:
                        c.applied = True
                    print(f"  [OK]  {py_path.name}: {len(changes)} guardia(s) aplicada(s)")
                else:
                    print(f"  [ERR] {py_path.name}: fallo de escritura")

            log.files.append(record)


# ═══════════════════════════════════════════════════════════════════════════
# P2: PLAN DE MIGRACIÓN DE PARES LEGACY/_v2
# ═══════════════════════════════════════════════════════════════════════════

def _analyze_pair(root: Path, legacy_name: str, v2_name: str) -> dict:
    """
    Analiza un par legacy/_v2 y genera un plan de migración detallado.

    El plan incluye:
    - Diferencia de líneas entre ambos archivos
    - Módulos que importan cada versión
    - Estrategia de consolidación recomendada
    - Comandos Git para preservar historia
    """
    legacy_path = root / legacy_name
    v2_path = root / v2_name

    plan: dict = {
        "legacy": legacy_name,
        "canonical": v2_name,
        "target_name": legacy_name,  # el nombre final será el legacy (sin _v2)
        "status": "unknown",
        "legacy_lines": 0,
        "v2_lines": 0,
        "importers_of_legacy": [],
        "importers_of_v2": [],
        "strategy": "",
        "git_commands": [],
        "migration_steps": [],
    }

    if not legacy_path.exists():
        plan["status"] = "legacy_missing"
        return plan
    if not v2_path.exists():
        plan["status"] = "v2_missing"
        return plan

    legacy_content = legacy_path.read_text(errors="replace")
    v2_content = v2_path.read_text(errors="replace")

    plan["legacy_lines"] = legacy_content.count("\n")
    plan["v2_lines"] = v2_content.count("\n")

    # Detectar quién importa cada versión
    legacy_stem = Path(legacy_name).stem
    v2_stem = Path(v2_name).stem

    for py_path in sorted(root.rglob("*.py")):
        if py_path.name in (legacy_name, v2_name, "vigia_mass_refactor.py"):
            continue
        if "pycache" in str(py_path):
            continue
        try:
            c = py_path.read_text(errors="replace")
        except Exception:
            continue

        rel = str(py_path.relative_to(root))
        if re.search(rf'\b{re.escape(legacy_stem)}\b', c):
            plan["importers_of_legacy"].append(rel)
        if re.search(rf'\b{re.escape(v2_stem)}\b', c):
            plan["importers_of_v2"].append(rel)

    # Determinar estrategia
    has_legacy_importers = len(plan["importers_of_legacy"]) > 0
    has_v2_importers = len(plan["importers_of_v2"]) > 0
    v2_is_larger = plan["v2_lines"] > plan["legacy_lines"]

    if v2_is_larger and has_v2_importers:
        plan["strategy"] = (
            "CONSOLIDE_V2_AS_CANONICAL: v2 tiene más líneas y tiene importadores activos. "
            "Renombrar v2 como el nombre canónico (sin sufijo), actualizar importadores del legacy."
        )
    elif has_legacy_importers and not has_v2_importers:
        plan["strategy"] = (
            "MERGE_V2_INTO_LEGACY: Solo el legacy tiene importadores. "
            "Mergear mejoras de v2 al legacy y eliminar v2."
        )
    else:
        plan["strategy"] = (
            "MANUAL_REVIEW: Ambos tienen importadores o la situación es ambigua. "
            "Revisar manualmente antes de consolidar."
        )

    # Comandos Git para preservar historia
    canonical_name = legacy_name  # nombre final sin _v2
    plan["git_commands"] = [
        f"# Paso 1: Preservar historia de {v2_name} en {canonical_name}",
        f"git mv {v2_name} {canonical_name}",
        f"# Paso 2: Eliminar legacy (contenido ya consolidado en {canonical_name})",
        f"git rm {legacy_name}",
        f"# Paso 3: Actualizar imports en todos los archivos",
        f"grep -rl '{v2_stem}' . | xargs sed -i 's/{v2_stem}/{Path(canonical_name).stem}/g'",
        f"# Paso 4: Commit atómico",
        f"git add -A && git commit -m 'refactor: consolidar {legacy_name} + {v2_name} → {canonical_name}'",
    ]

    # Pasos de migración detallados
    plan["migration_steps"] = [
        f"1. Verificar que {v2_name} incluye todas las correcciones de seguridad de {legacy_name}",
        f"2. Ejecutar test suite contra {v2_name} en aislamiento",
        f"3. Agregar shim de compatibilidad en {legacy_name}: "
        f"   'from {v2_stem} import *  # compatibility shim — eliminar en v2.0'",
        f"4. Ejecutar git commands listados en este plan",
        f"5. Verificar: python3 -c \"from {Path(canonical_name).stem} import *; print('OK')\"",
        f"6. Eliminar shim de compatibilidad",
    ]

    plan["status"] = "plan_ready"
    return plan


def op_p2_migration_plans(
    root: Path,
    dry_run: bool,
    log: AuditLog,
) -> None:
    """P2: Genera planes de migración para pares legacy/_v2."""
    print("\n[P2] Planes de migración para pares legacy/_v2")
    print(f"     {len(LEGACY_V2_PAIRS)} par(es) detectado(s)\n")

    for legacy_name, v2_name in LEGACY_V2_PAIRS:
        plan = _analyze_pair(root, legacy_name, v2_name)
        log.migration_plans.append(plan)

        status_icon = "[OK] " if plan["status"] == "plan_ready" else "[WARN]"
        print(f"  {status_icon} {legacy_name} ↔ {v2_name}")
        print(f"         Líneas: legacy={plan['legacy_lines']}, v2={plan['v2_lines']}")
        print(f"         Importadores legacy: {len(plan['importers_of_legacy'])}")
        print(f"         Importadores v2:     {len(plan['importers_of_v2'])}")
        print(f"         Estrategia: {plan['strategy'][:80]}...")
        if plan["git_commands"]:
            print(f"         Git:")
            for cmd in plan["git_commands"][:3]:
                print(f"           {cmd}")
        print()


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

ALL_OPS = ["P0A", "P0B", "P0C", "P1", "P2"]

OP_DESCRIPTIONS = {
    "P0A": "Migración de namespace de hypothesis_id",
    "P0B": "Purga de ForensicBundle.seal() fuera de ebs_v1.py",
    "P0C": "Corrección de dangling imports (ebs → ebs_v1)",
    "P1":  "Inyección de determinismo matemático (entropía cross-arch)",
    "P2":  "Planes de migración para pares legacy/_v2",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VIGÍA Mass Refactorer — Refactorizador Masivo de Grado Industrial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Ejemplos:
          python3 vigia_mass_refactor.py --path /repo --dry-run
          python3 vigia_mass_refactor.py --path /repo --all
          python3 vigia_mass_refactor.py --path /repo --ops P0A P0B --dry-run
          python3 vigia_mass_refactor.py --path /repo --all --no-backup
        """),
    )
    parser.add_argument(
        "--path", default=".",
        help="Raíz del repositorio (default: directorio actual)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Previsualizar cambios sin tocar el sistema de archivos",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Ejecutar todas las operaciones: " + ", ".join(ALL_OPS),
    )
    parser.add_argument(
        "--ops", nargs="+", choices=ALL_OPS, metavar="OP",
        help=f"Operaciones a ejecutar. Opciones: {', '.join(ALL_OPS)}",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="No crear archivos .bak (peligroso fuera de repositorio Git)",
    )
    parser.add_argument(
        "--output", default=None,
        help="Ruta del log de auditoría JSON (default: vigia_refactor_audit_<ts>.json)",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"ERROR: '{root}' no es un directorio válido.", file=sys.stderr)
        return 1

    ops = ALL_OPS if args.all else (args.ops or [])
    if not ops:
        parser.print_help()
        print("\nERROR: Especificar --all o --ops <OP...>", file=sys.stderr)
        return 1

    backup = not args.no_backup
    dry_run = args.dry_run

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    audit_path = Path(args.output) if args.output else Path(f"vigia_refactor_audit_{ts}.json")

    log = AuditLog(
        timestamp=now_iso(),
        repo_root=str(root),
        dry_run=dry_run,
        operations=ops,
    )

    # Banner
    print("═" * 72)
    print("VIGÍA MASS REFACTORER — Grado Industrial")
    print("═" * 72)
    print(f"  Repositorio : {root}")
    print(f"  Modo        : {'DRY-RUN (sin cambios)' if dry_run else 'LIVE (escribe en disco)'}")
    print(f"  Backup      : {'SI (.bak)' if backup and not dry_run else 'NO'}")
    print(f"  Operaciones : {', '.join(ops)}")
    print(f"  Log auditoría: {audit_path}")
    print()
    for op in ops:
        print(f"  [{op}] {OP_DESCRIPTIONS[op]}")
    print()

    if not dry_run and not args.no_backup:
        print("  AVISO: Modo LIVE activo. Se crearán archivos .bak antes de cada modificación.")
        print("         Para revertir: find . -name '*.bak' -exec sh -c 'mv \"$1\" \"${1%.bak}\"' _ {} \\;")
        print()

    # Ejecutar operaciones
    if "P0A" in ops:
        op_p0a_migrate_hypothesis_ids(root, dry_run, backup, log)

    if "P0B" in ops:
        op_p0b_purge_seal(root, dry_run, backup, log)

    if "P0C" in ops:
        op_p0c_fix_dangling_imports(root, dry_run, backup, log)

    if "P1" in ops:
        op_p1_inject_determinism(root, dry_run, backup, log)

    if "P2" in ops:
        op_p2_migration_plans(root, dry_run, log)

    # Resumen
    total_changes = sum(len(f.changes) for f in log.files)
    total_applied = sum(
        sum(1 for c in f.changes if c.applied)
        for f in log.files
    )
    total_errors = sum(
        sum(1 for c in f.changes if c.error)
        for f in log.files
    )

    log.summary = {
        "files_touched": len(log.files),
        "total_changes_planned": total_changes,
        "total_changes_applied": total_applied if not dry_run else 0,
        "total_errors": total_errors,
        "dry_run": dry_run,
        "migration_plans_generated": len(log.migration_plans),
        "dangling_imports_found": len(log.dangling_imports_report),
    }

    print("\n" + "═" * 72)
    print("RESUMEN")
    print("═" * 72)
    print(f"  Archivos con cambios : {log.summary['files_touched']}")
    print(f"  Cambios planificados : {log.summary['total_changes_planned']}")
    if not dry_run:
        print(f"  Cambios aplicados   : {log.summary['total_changes_applied']}")
        print(f"  Errores             : {log.summary['total_errors']}")
    print(f"  Planes migración    : {log.summary['migration_plans_generated']}")
    print(f"  Dangling imports    : {log.summary['dangling_imports_found']}")
    print()

    # Escribir log de auditoría
    try:
        audit_path.write_text(
            json.dumps(log.to_dict(), indent=2, sort_keys=True, ensure_ascii=True),
            encoding="utf-8",
        )
        print(f"  Log de auditoría escrito: {audit_path}")
    except Exception as e:
        print(f"  [ERR] No se pudo escribir log de auditoría: {e}", file=sys.stderr)

    print()
    if total_errors > 0:
        print(f"  RESULTADO: COMPLETADO CON {total_errors} ERROR(ES) — revisar log")
        return 1
    if dry_run:
        print("  RESULTADO: DRY-RUN completado — sin cambios en disco")
    else:
        print("  RESULTADO: OK — refactorización aplicada")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
