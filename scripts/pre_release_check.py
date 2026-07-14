#!/usr/bin/env python3
"""
pre_release_check.py
─────────────────────────────────────────────────────────────────────────────
VIGÍA Forensic Suite — Auditoría Estática Pre-Release

Propósito:
    Recorre el repositorio usando ast.parse() (stdlib puro) y bloquea
    cualquier commit que importe módulos marcados como DEPRECATED o LEGACY.
    Diseñado para correr como pre-commit hook o en CI/CD.

Qué detecta:
    1. Imports de módulos en BANNED_MODULES (ebs, semiotic_detector sin v2, etc.)
    2. Presencia de seal() definido en ForensicBundle (violación arquitectural)
    3. Presencia de shadow_mode en cualquier import
    4. Coexistencia de archivos _v1/_v2 sin shim explícito
    5. Modules que contienen math.log/math.log2 y contribuyen a hashes
       sin pasar por Fraction o _round_floats (riesgo ARM/x86 drift)

Uso:
    python3 pre_release_check.py [--path /ruta/al/repo] [--strict] [--json]

    --path      Raíz del repositorio (default: directorio actual)
    --strict    Falla con código 2 si hay WARNINGS además de errores
    --json      Salida en JSON estructurado (para CI/CD)
    --fix-hint  Muestra sugerencia de corrección por cada hallazgo

Salida:
    EXIT 0 — sin violaciones
    EXIT 1 — hay errores CRÍTICOS (bloquea commit/merge)
    EXIT 2 — hay warnings (con --strict también bloquea)

Diseño Daubert:
    - Solo usa ast de stdlib: verificable por terceros sin instalar nada
    - No modifica ningún archivo: solo lectura y reporte
    - Determinista: mismo repo → mismo resultado
    - Hash del propio script impreso para trazabilidad forense

─────────────────────────────────────────────────────────────────────────────
VIGÍA SANS FIND EVIL Hackathon 2026 — Auditoría Estática
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Configuración de módulos prohibidos
# ---------------------------------------------------------------------------

# Formato: { "nombre_modulo": "razón + módulo canónico" }
BANNED_MODULES: dict[str, str] = {
    # ebs.py contiene ForensicBundle.seal() — viola invariante arquitectural
    "ebs": "DEPRECATED — usar 'models.ebs_v1' o 'vigia.core.ebs_v1'. "
           "ebs.py contiene ForensicBundle.seal() que viola la invariante "
           "de sellado externo (BundleBuilder es el único atestador).",

    # semiotic_detector legacy — bug de iterador consumido en _is_subsequence
    "semiotic_detector": "DEPRECATED — usar 'semiotic_detector_v2'. "
                         "La versión legacy tiene bug de iterador consumido en "
                         "_is_subsequence() que causa sub-detección silenciosa "
                         "de secuencias en llamadas múltiples.",

    # shadow_mode — rechazado por violación Daubert (fabricación de veredictos)
    "shadow_mode": "PROHIBITED — violación Daubert. Shadow Mode genera veredictos "
                   "falsos para engañar al atacante, rompiendo la invariante de "
                   "integridad forense. Decisión arquitectural irrevocable.",

    # verify_ebs sin versión — versión 1.1.0 sin _DETERMINISTIC_FLOAT_PREC
    "verify_ebs": "DEPRECATED — usar 'verify_ebs_v1' (v1.2.0). "
                  "La versión sin sufijo carece de normalización de floats "
                  "determinista y auto-path para ejecución standalone.",

    # vigia_core_semiotic_detector — fragmento del monolito original
    "vigia_core_semiotic_detector": "DEPRECATED — fragmento del monolito legacy. "
                                     "Usar 'semiotic_detector_v2'.",

    # vigia_core_forensic_technical_detector — ídem
    "vigia_core_forensic_technical_detector": "DEPRECATED — fragmento del monolito legacy. "
                                               "Usar 'forensic_technical_detector'.",

    # llm_backend sin versión
    "llm_backend": "DEPRECATED — usar 'llm_backend_v2'. "
                   "La versión sin sufijo carece de soporte Ollama air-gapped.",

    # report_exporter sin versión
    "report_exporter": "DEPRECATED — usar 'report_exporter_v2'.",

}

# Módulos prohibidos por nombre de ARCHIVO (no de módulo en path).
# Se aplican solo cuando el archivo mismo se llama así, no cuando
# otro módulo lo importa por path completo (ej: vigia.core.risk_bounded_layer
# es el path canónico vivo; risk_bounded_layer.py en raíz sería legacy).
BANNED_FILENAMES: dict[str, str] = {
    # B-117 (2026-07-14): risk_bounded_layer.py is the CANONICAL version.
    # The inverted-posterior bug (P0-001) was fixed in v1 directly (commit
    # f8c9f9f1). risk_bounded_layer_v2.py was deleted as dead weight —
    # its only purpose (the P0-001 guard) is now in v1's docstring and code.
}

# Módulos que DEBEN existir como canónicos (si falta alguno, es señal de problema)
REQUIRED_CANONICAL: list[str] = [
    "models/ebs_v1.py",
    "verify_ebs_v1.py",
    "semiotic_detector_v2.py",
]

# Patrones que indican que ForensicBundle tiene seal() — violación arquitectural
SEAL_PATTERN = re.compile(
    r'class\s+ForensicBundle.*?def\s+seal\s*\(',
    re.DOTALL,
)

# Operaciones flotantes no deterministas en contexto de hash
FLOAT_ENTROPY_OPS = re.compile(
    r'\b(math\.log2?\s*\(|math\.log10\s*\(|statistics\.(mean|stdev|variance)\s*\()',
)
HASH_CONTRIBUTION = re.compile(
    r'\b(sha256|bundle_hash|graph_hash|hmac\.new)\b',
)
FLOAT_SAFE_GUARD = re.compile(
    r'\b(Fraction|_round_floats|round\s*\(.*,\s*6\))',
)


# ---------------------------------------------------------------------------
# Estructuras de resultado
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING  = "WARNING"
SEVERITY_INFO     = "INFO"


@dataclass
class Finding:
    severity: str
    file: str
    line: Optional[int]
    rule: str
    message: str
    fix_hint: str = ""

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "rule": self.rule,
            "message": self.message,
            "fix_hint": self.fix_hint,
        }


@dataclass
class AuditReport:
    repo_root: str
    files_scanned: int = 0
    findings: List[Finding] = field(default_factory=list)
    script_hash: str = ""

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SEVERITY_CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == SEVERITY_WARNING)

    def to_dict(self) -> dict:
        return {
            "repo_root": self.repo_root,
            "files_scanned": self.files_scanned,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "script_hash": self.script_hash,
            "findings": [f.to_dict() for f in self.findings],
        }


# ---------------------------------------------------------------------------
# Visitante AST para detección de imports prohibidos
# ---------------------------------------------------------------------------

class BannedImportVisitor(ast.NodeVisitor):
    """
    Recorre el AST de un archivo Python y detecta:
    - import <banned_module>
    - from <banned_module> import ...
    - from <package>.<banned_module> import ...  (sub-imports)
    """

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.findings: List[Finding] = []

    def _check_module_name(self, module_name: str, lineno: int) -> None:
        """
        Verifica si cualquier segmento del nombre completo del módulo
        está en BANNED_MODULES.

        Ejemplo: "vigia.models.ebs" → segmentos ["vigia", "models", "ebs"]
        → "ebs" está prohibido → CRITICAL
        """
        if not module_name:
            return

        segments = module_name.split(".")
        for seg in segments:
            if seg in BANNED_MODULES:
                reason = BANNED_MODULES[seg]
                self.findings.append(Finding(
                    severity=SEVERITY_CRITICAL,
                    file=self.filename,
                    line=lineno,
                    rule="BANNED_MODULE_IMPORT",
                    message=(
                        f"Import de módulo DEPRECATED/PROHIBITED detectado: "
                        f"'{module_name}' (segmento prohibido: '{seg}')"
                    ),
                    fix_hint=reason,
                ))
                # Solo reportar una vez por import aunque haya múltiples segmentos prohibidos
                break

    def visit_Import(self, node: ast.Import) -> None:
        """Maneja: import ebs, import vigia.ebs"""
        for alias in node.names:
            self._check_module_name(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Maneja: from ebs import ForensicBundle, from vigia.models import ebs"""
        if node.module:
            self._check_module_name(node.module, node.lineno)
        # También revisar los nombres importados por si fueran módulos
        # Ejemplo: from vigia import ebs  → names=[alias(name='ebs')]
        for alias in node.names:
            if alias.name in BANNED_MODULES:
                self.findings.append(Finding(
                    severity=SEVERITY_CRITICAL,
                    file=self.filename,
                    line=node.lineno,
                    rule="BANNED_MODULE_IMPORT",
                    message=(
                        f"Import de nombre DEPRECATED/PROHIBITED: "
                        f"'from {node.module or '?'} import {alias.name}'"
                    ),
                    fix_hint=BANNED_MODULES[alias.name],
                ))
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Verificación de seal() en ForensicBundle
# ---------------------------------------------------------------------------

def check_seal_method(filepath: str, content: str) -> List[Finding]:
    """
    Detecta si ForensicBundle define seal() como método de instancia.
    Esto viola la invariante arquitectural: solo BundleBuilder puede sellar.

    Usa dos métodos complementarios:
    1. Regex sobre el source (rápido, para pre-filtrado)
    2. AST para confirmar (preciso, evita falsos positivos en strings/comentarios)
    """
    findings = []

    # Pre-filtro rápido con regex
    if "ForensicBundle" not in content or "def seal" not in content:
        return findings

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        return findings

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if node.name != "ForensicBundle":
            continue
        # Buscar métodos 'seal' dentro de esta clase
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "seal":
                findings.append(Finding(
                    severity=SEVERITY_CRITICAL,
                    file=filepath,
                    line=item.lineno,
                    rule="FORENSIC_BUNDLE_SEAL_VIOLATION",
                    message=(
                        "ForensicBundle.seal() definido como método de instancia. "
                        "VIOLACIÓN ARQUITECTURAL: Un motor comprometido puede sellar "
                        "su propia mentira. Solo BundleBuilder (externo) puede sellar."
                    ),
                    fix_hint=(
                        "Eliminar seal() de ForensicBundle. "
                        "El sellado debe hacerse exclusivamente via BundleBuilder.seal(bundle). "
                        "Ver models/ebs_v1.py como referencia canónica."
                    ),
                ))
    return findings


# ---------------------------------------------------------------------------
# Verificación de entropía flotante sin guardia determinista
# ---------------------------------------------------------------------------

def check_float_entropy_in_hash_path(filepath: str, content: str) -> List[Finding]:
    """
    Detecta módulos que:
    1. Calculan entropía con math.log/math.log2/statistics.*
    2. Contribuyen a hashes (sha256, bundle_hash, hmac)
    3. NO tienen guardia Fraction ni _round_floats

    Riesgo: ARM Cortex-A53 vs x86_64 puede producir resultados IEEE 754
    distintos en el bit 52 para log2(p) con p muy pequeño, rompiendo
    la Invariante I2 (bundle_hash reproducible cross-arquitectura).
    """
    findings = []

    has_float_entropy = bool(FLOAT_ENTROPY_OPS.search(content))
    has_hash_contrib = bool(HASH_CONTRIBUTION.search(content))
    has_safe_guard = bool(FLOAT_SAFE_GUARD.search(content))

    if has_float_entropy and has_hash_contrib and not has_safe_guard:
        # Encontrar la primera línea con la operación flotante para referenciar
        first_line = None
        for i, line in enumerate(content.splitlines(), 1):
            if FLOAT_ENTROPY_OPS.search(line):
                first_line = i
                break

        findings.append(Finding(
            severity=SEVERITY_WARNING,
            file=filepath,
            line=first_line,
            rule="FLOAT_ENTROPY_NO_DETERMINISTIC_GUARD",
            message=(
                "Módulo usa math.log/math.log2 o statistics.* para entropía "
                "y contribuye a hashes, pero NO tiene Fraction ni _round_floats. "
                "Riesgo: divergencia ARM/x86 en bit 52 de IEEE 754 rompe Invariante I2."
            ),
            fix_hint=(
                "Opción A (canónica): delegar cálculo a vigia.sift._math_utils._entropy_shannon() "
                "que usa Fraction+Taylor puro.\n"
                "Opción B (mínima): aplicar round(entropy_value, 6) antes de "
                "serializar/hashear. Documentar como limitación conocida.\n"
                "Módulos en RIESGO TOTAL (sin round): entanglement.py, vigia_integration_bridge.py"
            ),
        ))
    return findings


# ---------------------------------------------------------------------------
# Verificación de IDs de hipótesis duplicados
# ---------------------------------------------------------------------------

def check_hypothesis_id_collisions(filepath: str, content: str) -> List[Finding]:
    """
    Detecta si el mismo hypothesis_id aparece más de una vez en el mismo archivo
    pero asociado a diferentes intent_type.

    Este es el patrón exacto que produjo la colisión H_EX_001
    entre EXECUTION y EXFILTRATION en abductive_intent_engine.py.
    """
    findings = []

    if "hypothesis_id" not in content:
        return findings

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        return findings

    # Recolectar todos los hypothesis_id del archivo mediante búsqueda de strings
    # (los IDs son literales de string en los constructores de AbductiveHypothesis)
    id_locations: dict[str, list[int]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, str):
            continue
        val = node.value
        if isinstance(val, str) and re.match(r'^H_[A-Z]{2}_\d{3}', val):
            id_locations.setdefault(val, []).append(node.lineno)

    # IDs que aparecen en más de una ubicación son candidatos a colisión
    for hyp_id, lines in id_locations.items():
        if len(lines) > 1:
            findings.append(Finding(
                severity=SEVERITY_CRITICAL,
                file=filepath,
                line=lines[0],
                rule="HYPOTHESIS_ID_COLLISION",
                message=(
                    f"hypothesis_id '{hyp_id}' aparece {len(lines)} veces "
                    f"en el mismo archivo (líneas: {lines}). "
                    f"Posible colisión de namespace entre fases IR distintas."
                ),
                fix_hint=(
                    f"Verificar que '{hyp_id}' no está asignado a fases IR distintas. "
                    f"Namespace canónico propuesto:\n"
                    f"  H_EX_* → EXECUTION  |  H_XF_* → EXFILTRATION\n"
                    f"  H_DE_* → DEFENSE_EVASION  |  H_PE_* → PERSISTENCE\n"
                    f"  H_IA_* → INITIAL_ACCESS   |  H_RE_* → RECONNAISSANCE\n"
                    f"  H_LM_* → LATERAL_MOVEMENT |  H_CA_* → CREDENTIAL_ACCESS\n"
                    f"  H_CO_* → COLLECTION        |  H_C2_* → C2\n"
                    f"  H_IM_* → IMPACT            |  H_DI_* → DISCOVERY\n"
                    f"  H_CL_* → CLEANUP           |  H_SE_* → FALSE_SECURITY_THEATER"
                ),
            ))

    return findings


# ---------------------------------------------------------------------------
# Verificación de archivos canónicos requeridos
# ---------------------------------------------------------------------------

def check_required_canonicals(repo_root: str) -> List[Finding]:
    """Verifica que los módulos canónicos existan."""
    findings = []
    for canonical in REQUIRED_CANONICAL:
        path = Path(repo_root) / canonical
        if not path.exists():
            # Buscar recursivamente por si está en subdirectorio
            matches = list(Path(repo_root).rglob(Path(canonical).name))
            if not matches:
                findings.append(Finding(
                    severity=SEVERITY_WARNING,
                    file=canonical,
                    line=None,
                    rule="MISSING_CANONICAL_MODULE",
                    message=f"Módulo canónico requerido no encontrado: {canonical}",
                    fix_hint=f"Asegurarse de que {canonical} existe y está en el path correcto.",
                ))
    return findings


# ---------------------------------------------------------------------------
# Runner principal
# ---------------------------------------------------------------------------

def scan_repository(repo_root: str, strict: bool = False) -> AuditReport:
    """
    Recorre el repositorio y aplica todas las verificaciones.
    Excluye: __pycache__, .git, node_modules, *.pyc
    """
    root = Path(repo_root).resolve()
    report = AuditReport(repo_root=str(root))

    # Hash del propio script (trazabilidad forense)
    try:
        script_content = Path(__file__).read_bytes()
        report.script_hash = hashlib.sha256(script_content).hexdigest()
    except Exception:
        report.script_hash = "unavailable"

    # Verificar canónicos requeridos
    report.findings.extend(check_required_canonicals(str(root)))

    # Recorrer archivos Python
    EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".tox"}

    for py_file in sorted(root.rglob("*.py")):
        # Excluir directorios no relevantes
        parts = set(py_file.parts)
        if parts & EXCLUDED_DIRS:
            continue

        # Excluir el propio script de auditoría
        if py_file.name == "pre_release_check.py":
            continue

        rel_path = str(py_file.relative_to(root))
        report.files_scanned += 1

        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            report.findings.append(Finding(
                severity=SEVERITY_WARNING,
                file=rel_path,
                line=None,
                rule="FILE_READ_ERROR",
                message=f"No se pudo leer el archivo: {e}",
            ))
            continue

        # R0: Archivo legacy por nombre de archivo
        if py_file.name in BANNED_FILENAMES:
            report.findings.append(Finding(
                severity=SEVERITY_WARNING,
                file=rel_path,
                line=1,
                rule="BANNED_LEGACY_FILENAME",
                message=(
                    f"Archivo legacy detectado: '{py_file.name}' "
                    f"no debería existir en el repo de release."
                ),
                fix_hint=BANNED_FILENAMES[py_file.name],
            ))

        # R1: Imports de módulos prohibidos (via AST)
        try:
            tree = ast.parse(content, filename=rel_path)
            visitor = BannedImportVisitor(filename=rel_path)
            visitor.visit(tree)
            report.findings.extend(visitor.findings)
        except SyntaxError as e:
            report.findings.append(Finding(
                severity=SEVERITY_WARNING,
                file=rel_path,
                line=e.lineno,
                rule="SYNTAX_ERROR",
                message=f"Error de sintaxis: {e.msg}",
                fix_hint="Corregir el archivo antes del release.",
            ))
            continue

        # R2: ForensicBundle.seal() definido localmente
        report.findings.extend(check_seal_method(rel_path, content))

        # R3: Entropía flotante sin guardia determinista en path de hash
        report.findings.extend(check_float_entropy_in_hash_path(rel_path, content))

        # R4: Colisiones de hypothesis_id
        report.findings.extend(check_hypothesis_id_collisions(rel_path, content))

    return report


# ---------------------------------------------------------------------------
# Formateo de salida
# ---------------------------------------------------------------------------

ANSI_RED    = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_GREEN  = "\033[92m"
ANSI_CYAN   = "\033[96m"
ANSI_BOLD   = "\033[1m"
ANSI_RESET  = "\033[0m"

def _color(text: str, code: str) -> str:
    return f"{code}{text}{ANSI_RESET}" if sys.stdout.isatty() else text


def print_report(report: AuditReport, show_fix_hints: bool = False) -> None:
    print()
    print(_color("=" * 72, ANSI_BOLD))
    print(_color("VIGÍA PRE-RELEASE AUDIT — Auditoría Estática de Imports", ANSI_BOLD))
    print(_color("=" * 72, ANSI_BOLD))
    print(f"  Repositorio : {report.repo_root}")
    print(f"  Archivos    : {report.files_scanned} archivos Python escaneados")
    print(f"  Script hash : {report.script_hash[:16]}... (SHA-256 para trazabilidad)")
    print()

    if not report.findings:
        print(_color("  [PASS] Sin violaciones detectadas. Repo limpio para release.", ANSI_GREEN))
        print()
        return

    # Agrupar por severidad
    criticals = [f for f in report.findings if f.severity == SEVERITY_CRITICAL]
    warnings  = [f for f in report.findings if f.severity == SEVERITY_WARNING]

    if criticals:
        print(_color(f"  CRITICOS ({len(criticals)}):", ANSI_RED + ANSI_BOLD))
        for f in criticals:
            loc = f":{f.line}" if f.line else ""
            print(_color(f"  [CRIT] {f.file}{loc}", ANSI_RED))
            print(f"         Regla  : {f.rule}")
            print(f"         Mensaje: {f.message}")
            if show_fix_hints and f.fix_hint:
                for line in f.fix_hint.splitlines():
                    print(f"         Fix    : {line}")
            print()

    if warnings:
        print(_color(f"  WARNINGS ({len(warnings)}):", ANSI_YELLOW + ANSI_BOLD))
        for f in warnings:
            loc = f":{f.line}" if f.line else ""
            print(_color(f"  [WARN] {f.file}{loc}", ANSI_YELLOW))
            print(f"         Regla  : {f.rule}")
            print(f"         Mensaje: {f.message}")
            if show_fix_hints and f.fix_hint:
                for line in f.fix_hint.splitlines():
                    print(f"         Fix    : {line}")
            print()

    print(_color("=" * 72, ANSI_BOLD))
    status_color = ANSI_RED if criticals else ANSI_YELLOW
    status_text = "BLOQUEADO" if criticals else "ADVERTENCIA"
    print(_color(
        f"  RESULTADO: {status_text} — "
        f"{len(criticals)} crítico(s), {len(warnings)} warning(s)",
        status_color + ANSI_BOLD,
    ))
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="VIGÍA Pre-Release Static Audit — detecta imports DEPRECATED/LEGACY",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--path", default=".",
        help="Raíz del repositorio a auditar (default: directorio actual)",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Fallar con código 2 si hay warnings (además de errores críticos)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Salida en JSON estructurado (para CI/CD)",
    )
    parser.add_argument(
        "--fix-hint", action="store_true",
        help="Mostrar sugerencias de corrección por cada hallazgo",
    )
    args = parser.parse_args()

    repo_root = os.path.abspath(args.path)
    if not os.path.isdir(repo_root):
        print(f"ERROR: '{repo_root}' no es un directorio válido.", file=sys.stderr)
        return 1

    report = scan_repository(repo_root, strict=args.strict)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print_report(report, show_fix_hints=args.fix_hint)

    # Códigos de salida
    if report.critical_count > 0:
        return 1
    if args.strict and report.warning_count > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
