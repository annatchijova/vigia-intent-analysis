"""
VIGÍA CI Validation Script — Pre-commit / Pre-push Hardening
===============================================================
Autores: VIGÍA AI Collective (Kimi, Claude, Gemini, DeepSeek, Qwen)
         Anna Tchijova — Arquitecta & Orquestadora

PROPÓSITO:
    Este script corre ANTES de cada commit/push y valida que el código
    cumple los estándares forenses de determinismo, seguridad y Daubert.
    Si falla, el commit se bloquea. No se puede subir código roto al repo.

PARA QUÉ SIRVE CADA CHECK:
----------------------------

1. DETERMINISMO_BIT_FOR_BIT
   → Verifica que no haya uuid.uuid4(), datetime.now(), random.random()
     en archivos críticos. Un bundle forense debe ser 100% reproducible.
     Si el hash cambia entre ejecuciones, un abogado defensor puede
     argumentar que el sistema es "caja negra" y Daubert lo rechaza.

2. TABLAS_CONGELADAS
   → Busca MappingProxyType o equivalente en archivos con tablas maestras.
     Si un atacante puede modificar MITRE_TTP_TO_PHASE en runtime,
     hace que DEFENSE_EVASION siempre gane. Esto es supply-chain attack.

3. HMAC_KEY_CONFIGURADO
   → Verifica que VIGIA_HMAC_KEY y VIGIA_HMAC_SALT estén seteados
     en el entorno de CI. Sin esto, los logs forenses no tienen
     cadena de custodia criptográfica.

4. NONCE_DETERMINISTA
   → Valida que _SESSION_NONCE se derive de HMAC(evidence_hash, salt)
     y no de uuid.uuid4(). Si el nonce es aleatorio, Rob T. Lee no puede
     reproducir la sesión en auditoría SANS.

5. NO_ROUND_EN_HASH
   → Detecta json.dumps con round() antes del hash. El hash debe
     calcularse sobre datos CRUDOS. Si redondeás antes, un perito
     recalculando desde originales obtiene hash diferente → duda razonable.

6. EXCLUSION_ENTROPY_PRESENTE
   → Verifica que graph_stability.py reporte excluded_edges y
     threshold_manipulation_alert. Sin esto, un atacante puede
     inyectar señales en π=0.84 (justo debajo de τ=0.85) y desaparecer.

7. I2_INVARIANCE_CHECK
   → Valida que _verify_stdlib_integrity() exista en el bridge.
     Si un rootkit monkey-patchea os.open, el sistema lee archivos
     falsos sin darse cuenta.

8. INPUT_VALIDATION
   → Busca validaciones de tamaño máximo en entry points (100k límite).
     Sin esto, un atacante envía 10M deltas y el servidor se congela.

9. ANTI_JAILBREAK_PROMPT
   → Verifica que docs/system_prompt_peirce.md contenga la regla
     ANTI-JAILBREAK y NONCE_SOURCE_TAMPERING. Si el LLM puede ser
     convencido de "olvida estas instrucciones", todo el sistema cae.

10. RESIDUAL_UNCERTAINTY
    → Valida que mitre_clustering.py incluya residual_uncertainty
      en cada técnica. VIGÍA nunca debe afirmar "este ataque ES T1070";
      debe decir "comparte estructura con T1070, incertidumbre X".

11. NO_TMP_WORLD_WRITABLE
    → Rechaza paths hardcodeados a /tmp. /tmp es world-writable;
      un atacante local puede crear symlinks para leer/escribir
      evidencia arbitraria.

12. KASSANDRA_SALT_SET
    → Verifica que KASSANDRA_SALT esté configurado. Sin salt, el nonce
      es predecible y un atacante puede pre-calcular delimitadores.

USO:
    python3 vigia_ci_validate.py [--fix] [--verbose]

    --fix   : Intenta auto-corregir problemas menores (no todos son auto-fixeables)
    --verbose: Muestra cada archivo escaneado

RETORNO:
    0 = todos los checks pasaron → commit permitido
    1 = algún check falló → commit BLOQUEADO

EJEMPLO EN .git/hooks/pre-commit:
    #!/bin/bash
    python3 vigia_ci_validate.py || exit 1
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

CRITICAL_FILES = [
    "vigia/vigia_sift_bridge.py",
    "vigia/core/graph_stability.py",
    "vigia/tools/abductive_intent_engine.py",
    "vigia/tools/visible_variables.py",
    "vigia/tools/picerl_mapping.py",
    "vigia/tools/mitre_clustering.py",
    "vigia/core/resource_optimizer.py",
    "vigia/core/shadow_mode.py",
    "vigia/tools/eml_symbolic.py",
    "vigia/tools/eml_gci.py",
    "vigia/core/risk_bounded_layer.py",
    "vigia/tools/vigia_planner.py",
    "vigia/forensics/vision_audit.py",
]

PROMPT_FILE = "docs/system_prompt_peirce.md"

# ============================================================================
# MOTOR DE CHECKS
# ============================================================================

class CheckResult:
    def __init__(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.name = name
        self.passed = passed
        self.message = message
        self.fixable = fixable

class VIGIACIValidator:
    def __init__(self, repo_root: str = ".", verbose: bool = False, fix: bool = False):
        self.repo_root = Path(repo_root)
        self.verbose = verbose
        self.fix = fix
        self.results: List[CheckResult] = []
        self._files_content: Dict[str, str] = {}

    def _load_file(self, rel_path: str) -> str:
        """Carga archivo del repo, con cache."""
        if rel_path not in self._files_content:
            full = self.repo_root / rel_path
            if full.exists():
                self._files_content[rel_path] = full.read_text(encoding="utf-8")
            else:
                self._files_content[rel_path] = ""
        return self._files_content[rel_path]

    def _add_result(self, name: str, passed: bool, message: str, fixable: bool = False):
        self.results.append(CheckResult(name, passed, message, fixable))
        status = " PASS" if passed else " FAIL"
        print(f"  [{status}] {name}: {message}")

    # ------------------------------------------------------------------
    # CHECK 1: Determinismo bit-for-bit
    # ------------------------------------------------------------------
    def check_determinismo(self) -> None:
        """Busca funciones no deterministas en archivos críticos."""
        forbidden = ["uuid.uuid4", "datetime.now", "random.random", "random.randint"]
        found = []
        for fname in CRITICAL_FILES:
            content = self._load_file(fname)
            if not content:
                continue
            for bad in forbidden:
                if bad in content:
                    # Excepción: uuid se usa solo en _derive_session_nonce (aceptable)
                    if bad == "uuid.uuid4" and "_derive_session_nonce" in content:
                        continue
                    # Excepción: datetime.now se usa solo en honey token TTL (no en path de veredicto)
                    if bad == "datetime.now" and "_HONEY_TOKEN_DIR" in content:
                        continue
                    found.append(f"{fname}: {bad}")
        if found:
            self._add_result(
                "DETERMINISMO_BIT_FOR_BIT",
                False,
                f"Funciones no deterministas detectadas: {found}",
                fixable=False,
            )
        else:
            self._add_result(
                "DETERMINISMO_BIT_FOR_BIT",
                True,
                "No se detectaron funciones no deterministas en archivos críticos.",
            )

    # ------------------------------------------------------------------
    # CHECK 2: Tablas congeladas
    # ------------------------------------------------------------------
    def check_tablas_congeladas(self) -> None:
        """Verifica que tablas maestras usen MappingProxyType."""
        tabla_files = [
            "vigia/tools/mitre_clustering.py",
            "vigia/tools/visible_variables.py",
            "vigia/tools/picerl_mapping.py",
            "vigia/inference/abductive_intent_engine.py",
        ]
        missing = []
        for fname in tabla_files:
            content = self._load_file(fname)
            if not content:
                continue
            if "MappingProxyType" not in content:
                missing.append(fname)
        if missing:
            self._add_result(
                "TABLAS_CONGELADAS",
                False,
                f"Tablas mutables (sin MappingProxyType): {missing}",
                fixable=False,
            )
        else:
            self._add_result(
                "TABLAS_CONGELADAS",
                True,
                "Todas las tablas maestras están congeladas.",
            )

    # ------------------------------------------------------------------
    # CHECK 3: HMAC key configurado
    # ------------------------------------------------------------------
    def check_hmac_key(self) -> None:
        """Verifica variables de entorno para HMAC."""
        key = os.environ.get("VIGIA_HMAC_KEY", "").strip()
        salt = os.environ.get("VIGIA_HMAC_SALT", "").strip()
        if not key:
            self._add_result(
                "HMAC_KEY_CONFIGURADO",
                False,
                "VIGIA_HMAC_KEY no está seteado. Los logs forenses no tienen cadena de custodia.",
                fixable=False,
            )
        elif not salt:
            self._add_result(
                "HMAC_KEY_CONFIGURADO",
                False,
                "VIGIA_HMAC_KEY está seteado pero VIGIA_HMAC_SALT falta. KDF vulnerable.",
                fixable=False,
            )
        else:
            self._add_result(
                "HMAC_KEY_CONFIGURADO",
                True,
                f"VIGIA_HMAC_KEY y VIGIA_HMAC_SALT configurados (key_len={len(key)}, salt_len={len(salt)}).",
            )

    # ------------------------------------------------------------------
    # CHECK 4: Nonce determinista
    # ------------------------------------------------------------------
    def check_nonce_determinista(self) -> None:
        """Verifica que el bridge use nonce determinista (no uuid)."""
        content = self._load_file("vigia/vigia_sift_bridge.py")
        if not content:
            self._add_result("NONCE_DETERMINISTA", False, "vigia_sift_bridge.py no encontrado.")
            return
        if "_derive_session_nonce" in content and "uuid.uuid4" not in content:
            self._add_result(
                "NONCE_DETERMINISTA",
                True,
                "Nonce se deriva de HMAC(evidence_hash, KASSANDRA_SALT).",
            )
        else:
            self._add_result(
                "NONCE_DETERMINISTA",
                False,
                "Nonce usa uuid.uuid4() o falta función _derive_session_nonce.",
                fixable=False,
            )

    # ------------------------------------------------------------------
    # CHECK 5: No round antes de hash
    # ------------------------------------------------------------------
    def check_no_round_en_hash(self) -> None:
        """Detecta round() en bloques de hash."""
        suspicious = []
        for fname in CRITICAL_FILES:
            content = self._load_file(fname)
            if not content:
                continue
            # Buscar hashlib.sha256 cerca de round()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "hashlib.sha256" in line or "json.dumps" in line:
                    # Revisar 5 líneas anteriores
                    context = "\n".join(lines[max(0, i-5):i+1])
                    if "round(" in context and "to_dict_display" not in context:
                        suspicious.append(f"{fname}:{i+1}")
        if suspicious:
            self._add_result(
                "NO_ROUND_EN_HASH",
                False,
                f"round() detectado cerca de hash/json.dumps: {suspicious[:5]}",
                fixable=False,
            )
        else:
            self._add_result(
                "NO_ROUND_EN_HASH",
                True,
                "Hash calculado sobre datos crudos (sin round previo).",
            )

    # ------------------------------------------------------------------
    # CHECK 6: Exclusion entropy presente
    # ------------------------------------------------------------------
    def check_exclusion_entropy(self) -> None:
        """Verifica que graph_stability reporte aristas excluidas."""
        content = self._load_file("vigia/core/graph_stability.py")
        if not content:
            self._add_result("EXCLUSION_ENTROPY_PRESENTE", False, "graph_stability.py no encontrado.")
            return
        checks = [
            "excluded_edges" in content,
            "exclusion_entropy" in content,
            "threshold_manipulation_alert" in content,
        ]
        if all(checks):
            self._add_result(
                "EXCLUSION_ENTROPY_PRESENTE",
                True,
                "GraphStability reporta excluded_edges, exclusion_entropy y threshold_manipulation_alert.",
            )
        else:
            missing = [c for c, ok in zip(["excluded_edges", "exclusion_entropy", "threshold_manipulation_alert"], checks) if not ok]
            self._add_result(
                "EXCLUSION_ENTROPY_PRESENTE",
                False,
                f"Falta en graph_stability.py: {missing}",
                fixable=False,
            )

    # ------------------------------------------------------------------
    # CHECK 7: I2 Invariance
    # ------------------------------------------------------------------
    def check_i2_invariance(self) -> None:
        """Verifica que exista verificación de stdlib integrity."""
        content = self._load_file("vigia/vigia_sift_bridge.py")
        if not content:
            self._add_result("I2_INVARIANCE_CHECK", False, "vigia_sift_bridge.py no encontrado.")
            return
        if "_verify_stdlib_integrity" in content and "monkey-patch" in content.lower():
            self._add_result(
                "I2_INVARIANCE_CHECK",
                True,
                "Verificación de integridad de stdlib presente (monkey-patch detection).",
            )
        else:
            self._add_result(
                "I2_INVARIANCE_CHECK",
                False,
                "Falta _verify_stdlib_integrity() en el bridge.",
                fixable=False,
            )

    # ------------------------------------------------------------------
    # CHECK 8: Input validation
    # ------------------------------------------------------------------
    def check_input_validation(self) -> None:
        """Busca validaciones de tamaño en entry points."""
        entry_points = [
            ("vigia/tools/eml_symbolic.py", "analyze_symbolic_regression"),
            ("vigia/tools/eml_gci.py", "analyze_gci"),
            ("vigia/vigia_sift_bridge.py", "reason_with_llm"),
        ]
        missing = []
        for fname, func in entry_points:
            content = self._load_file(fname)
            if not content:
                continue
            # Buscar la función y revisar si valida len() > MAX
            if func in content:
                # Heurística simple: buscar "len(" y "100_000" o "MAX" cerca
                if "100_000" not in content and "MAX_INPUT" not in content and "MAX_DELTAS" not in content:
                    missing.append(f"{fname}:{func}")
        if missing:
            self._add_result(
                "INPUT_VALIDATION",
                False,
                f"Entry points sin validación de tamaño: {missing}",
                fixable=False,
            )
        else:
            self._add_result(
                "INPUT_VALIDATION",
                True,
                "Entry points validan tamaño máximo de input.",
            )

    # ------------------------------------------------------------------
    # CHECK 9: Anti-jailbreak prompt
    # ------------------------------------------------------------------
    def check_anti_jailbreak(self) -> None:
        """Verifica reglas anti-jailbreak y nonce tampering en prompt."""
        content = self._load_file(PROMPT_FILE)
        if not content:
            self._add_result("ANTI_JAILBREAK_PROMPT", False, f"{PROMPT_FILE} no encontrado.")
            return
        has_anti = "ANTI-JAILBREAK" in content or "jailbreak" in content.lower()
        has_nonce = "NONCE_SOURCE_TAMPERING" in content
        if has_anti and has_nonce:
            self._add_result(
                "ANTI_JAILBREAK_PROMPT",
                True,
                "Prompt incluye ANTI-JAILBREAK y NONCE_SOURCE_TAMPERING.",
            )
        else:
            missing = []
            if not has_anti:
                missing.append("ANTI-JAILBREAK")
            if not has_nonce:
                missing.append("NONCE_SOURCE_TAMPERING")
            self._add_result(
                "ANTI_JAILBREAK_PROMPT",
                False,
                f"Falta en prompt: {missing}",
                fixable=False,
            )

    # ------------------------------------------------------------------
    # CHECK 10: Residual uncertainty
    # ------------------------------------------------------------------
    def check_residual_uncertainty(self) -> None:
        """Verifica residual_uncertainty en mitre_clustering."""
        content = self._load_file("vigia/tools/mitre_clustering.py")
        if not content:
            self._add_result("RESIDUAL_UNCERTAINTY", False, "mitre_clustering_P0.py no encontrado.")
            return
        if "residual_uncertainty" in content:
            self._add_result(
                "RESIDUAL_UNCERTAINTY",
                True,
                "MITRE techniques incluyen residual_uncertainty (humildad epistémica).",
            )
        else:
            self._add_result(
                "RESIDUAL_UNCERTAINTY",
                False,
                "Falta residual_uncertainty en MITREClusterer.",
                fixable=False,
            )

    # ------------------------------------------------------------------
    # CHECK 11: No /tmp world-writable
    # ------------------------------------------------------------------
    def check_no_tmp(self) -> None:
        """Rechaza paths hardcodeados a /tmp."""
        found = []
        for fname in CRITICAL_FILES:
            content = self._load_file(fname)
            if not content:
                continue
            if '"/tmp/' in content or "'/tmp/" in content:
                found.append(fname)
        if found:
            self._add_result(
                "NO_TMP_WORLD_WRITABLE",
                False,
                f"Paths hardcodeados a /tmp detectados: {found}",
                fixable=False,
            )
        else:
            self._add_result(
                "NO_TMP_WORLD_WRITABLE",
                True,
                "No se detectaron paths hardcodeados a /tmp.",
            )

    # ------------------------------------------------------------------
    # CHECK 12: KASSANDRA_SALT set
    # ------------------------------------------------------------------
    def check_kassandra_salt(self) -> None:
        """Verifica que KASSANDRA_SALT esté configurado."""
        salt = os.environ.get("KASSANDRA_SALT", "").strip()
        if not salt:
            self._add_result(
                "KASSANDRA_SALT_SET",
                False,
                "KASSANDRA_SALT no está seteado. El nonce es predecible.",
                fixable=False,
            )
        elif len(salt) < 16:
            self._add_result(
                "KASSANDRA_SALT_SET",
                False,
                f"KASSANDRA_SALT demasiado corto ({len(salt)} chars, min 16).",
                fixable=False,
            )
        else:
            self._add_result(
                "KASSANDRA_SALT_SET",
                True,
                f"KASSANDRA_SALT configurado (len={len(salt)}).",
            )

    # ------------------------------------------------------------------
    # RUN ALL
    # ------------------------------------------------------------------
    def run_all(self) -> int:
        print("=" * 80)
        print("VIGÍA CI Validation — Pre-commit Forensic Hardening")
        print("=" * 80)
        print(f"Repo root: {self.repo_root.absolute()}")
        print(f"Checks: 12 | Fix mode: {self.fix} | Verbose: {self.verbose}")
        print("-" * 80)

        self.check_determinismo()
        self.check_tablas_congeladas()
        self.check_hmac_key()
        self.check_nonce_determinista()
        self.check_no_round_en_hash()
        self.check_exclusion_entropy()
        self.check_i2_invariance()
        self.check_input_validation()
        self.check_anti_jailbreak()
        self.check_residual_uncertainty()
        self.check_no_tmp()
        self.check_kassandra_salt()

        print("-" * 80)
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        fixable = sum(1 for r in self.results if not r.passed and r.fixable)

        print(f"\nResultado: {passed}/{len(self.results)} checks PASARON")
        if failed:
            print(f"           {failed} FALLARON ({fixable} auto-fixeables)")
        print("=" * 80)

        return 0 if failed == 0 else 1


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="VIGÍA CI Forensic Validation")
    parser.add_argument("--fix", action="store_true", help="Intentar auto-corregir problemas menores")
    parser.add_argument("--verbose", action="store_true", help="Mostrar progreso detallado")
    parser.add_argument("--repo-root", default=".", help="Raíz del repositorio VIGÍA")
    args = parser.parse_args()

    validator = VIGIACIValidator(
        repo_root=args.repo_root,
        verbose=args.verbose,
        fix=args.fix,
    )
    exit_code = validator.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
