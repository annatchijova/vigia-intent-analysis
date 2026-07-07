"""
forensics/verify_ebs_v1.py
─────────────────────────────────────────────────────────────────────────────
Verificador Independiente EBS v1 — VIGIA Forensic Suite

GARANTIA DE INDEPENDENCIA TOTAL (DeepSeek + Gemini):
    Este script usa EXCLUSIVAMENTE stdlib Python.
    No importa NINGUNA clase de vigia.models, vigia.engine ni vigia.forensics.
    Puede ejecutarse en cualquier maquina con Python 3.6+ sin instalacion.
    Si el verificador necesita importar el codigo de produccion, el sistema
    no es auditable por terceros — viola el principio de independencia forense.

CONSTANTES LOCALES:
    Las constantes del estandar (EBS_VERSION, umbrales) estan copiadas aqui.
    No se importan desde ebs_v1.py. Esto es intencional: el verificador
    no debe depender de que el codigo de produccion este disponible.

VALIDACIONES R1-R5:
    R1 — Integridad de hashes (bundle_hash, graph_hash, policy_hash)
    R2 — Cumplimiento de politica (max_delta, allowed_roles)
    R3 — Coherencia de decision (risk <-> epsilon <-> ACCEPT/REJECT/ABSTAIN)
    R4 — engine_attestation_hash (si presente)
    R5 — Anclaje ECL (External Constraint Layer, si presente)

NIVELES DE CONFORMIDAD:
    Level 0 — Non-compliant:         estructura invalida
    Level 1 — Structurally valid:    esquema correcto
    Level 2 — Cryptographically valid: hashes consistentes + politica OK
    Level 3 — Fully compliant EBS v1:  R1-R5 + ECL presente

USO:
    python3 verify_ebs_v1.py bundle.json
    python3 verify_ebs_v1.py bundle.json --verbose
    python3 verify_ebs_v1.py bundle.json --strict   # falla si Level < 3
    python3 verify_ebs_v1.py bundle.json --json     # salida JSON estructurada
    echo $?  # 0=PASS  1=FAIL

PROTOCOLO DE HASH (identico a bundle_builder.py):
    graph_hash  = SHA256(evidence_graph SIN el campo graph_hash)
    policy_hash = SHA256(policy_spec)
    bundle_hash = SHA256(bundle_id + version + timestamp +
                         evidence_graph_CON_graph_hash + decision_trace +
                         policy_spec + actions + system_state)
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

# STDLIB ONLY — cero imports de produccion
import argparse
import os as _os
import sys as _sys
# Auto-path: agregar raíz del repo para imports standalone
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO_ROOT = _os.path.dirname(_HERE)  # tests/ -> repo/
if _REPO_ROOT not in _sys.path:
    _sys.path.insert(0, _REPO_ROOT)
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constantes locales del estandar EBS v1
# Copiadas deliberadamente — no se importan desde ebs_v1.py
# ---------------------------------------------------------------------------

_EBS_VERSION = "1.0"
_EBS_SUPPORTED_VERSIONS = ["1.0"]
_VERIFIER_VERSION = "1.3.0"   # bumped: signed-zero normalization (-0.0 == 0.0)


# ---------------------------------------------------------------------------
# Normalizacion determinista de floats — P0-1 (Kimi audit)
# Debe ser IDENTICA a bundle_builder._round_floats para hash cross-OS.
# ---------------------------------------------------------------------------
_DETERMINISTIC_FLOAT_PREC = 6


# Implementación standalone de _canonicalize/_sha256_dict
# Copiada de vigia/core/bundle_builder.py para funcionar sin PYTHONPATH
# Lockstep con vigia/core/canonicalize.py (R3-2): v2 default, v1 legacy.
import unicodedata as _unicodedata
from fractions import Fraction as _Fraction

_V2_STR_PREFIX = "s:"


def _v2_norm_str(s):
    return _unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n"))


def _canonicalize_v1(obj: Any) -> Any:
    """Esquema v1 (LEGACY — solo verificacion de bundles historicos)."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return obj
    if obj is None:
        return "null"
    if isinstance(obj, dict):
        return {k: _canonicalize_v1(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v1(v) for v in obj]
    return str(obj)


def _canonicalize_v2(obj: Any) -> Any:
    """Esquema v2 (R3-2) — DEFAULT. Escalares identicos a v1; strings escapados
    (s: + NFC/CRLF->LF); Fraction explicito. Cierra las colisiones de tipo."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:
            return "nan"
        if obj == float("inf"):
            return "inf"
        if obj == float("-inf"):
            return "-inf"
        return f"{obj + 0.0:.8f}"  # +0.0 maps -0.0 -> 0.0: signed zero must canonicalize identically
    if isinstance(obj, str):
        return _V2_STR_PREFIX + _v2_norm_str(obj)
    if obj is None:
        return "null"
    if isinstance(obj, _Fraction):
        return f"{obj.numerator}/{obj.denominator}:frac"
    if isinstance(obj, dict):
        return {k: _canonicalize_v2(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v2(v) for v in obj]
    return _V2_STR_PREFIX + _v2_norm_str(str(obj))


def _canonicalize(obj: Any) -> Any:
    """Forma canonica DEFAULT (v2). Ver vigia/core/canonicalize.py."""
    return _canonicalize_v2(obj)


def _sha256_dict(obj: Dict) -> str:
    """
    SHA-256 determinístico de un dict con forma canónica estricta (H22).

    Usa _canonicalize() antes de serializar para garantizar que
    int(1) y float(1.0) produzcan hashes distintos y reproducibles
    entre arquitecturas y versiones de Python.
    """
    canonical = _canonicalize(obj)
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

def _round_floats(obj: Any) -> Any:
    """
    Normalizacion recursiva de floats para hashing determinista cross-OS.
    Aplicar SIEMPRE antes de json.dumps en contexto de hash.
    """
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return str(obj)  # "nan" / "inf" — reproducible
        return round(obj, _DETERMINISTIC_FLOAT_PREC)
    if isinstance(obj, dict):
        return {k: _round_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v) for v in obj]
    return obj


# ---------------------------------------------------------------------------
# Hash helper — implementacion local, identica a bundle_builder._sha256_dict
# ---------------------------------------------------------------------------

def _sha256_dict(obj: Dict) -> str:
    """SHA-256 determinístico — usa _canonicalize() igual que bundle_builder."""
    canonical = _canonicalize(obj)
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True).encode('utf-8')
    return hashlib.sha256(serialized).hexdigest()


# ---------------------------------------------------------------------------
# Resultado de verificacion
# ---------------------------------------------------------------------------

class VerificationResult:

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []
        self.conformity_level: int = 0
        self.passed: bool = False
        self.timestamp: str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def add(
        self,
        rule: str,
        passed: bool,
        message: str,
        severity: str = "ERROR",
        detail: Optional[Any] = None,
    ) -> None:
        self.checks.append({
            "rule": rule,
            "passed": passed,
            "message": message,
            "severity": severity,
            "detail": detail,
        })

    def critical_failures(self) -> List[Dict]:
        return [c for c in self.checks if not c["passed"] and c["severity"] == "ERROR"]

    def to_dict(self) -> Dict[str, Any]:
        labels = {
            0: "Non-compliant",
            1: "Structurally valid",
            2: "Cryptographically valid",
            3: "Fully compliant EBS v1",
        }
        return {
            "verifier_version": _VERIFIER_VERSION,
            "timestamp": self.timestamp,
            "passed": self.passed,
            "conformity_level": self.conformity_level,
            "conformity_label": labels.get(self.conformity_level, "Unknown"),
            "checks": self.checks,
            "summary": {
                "total": len(self.checks),
                "passed": sum(1 for c in self.checks if c["passed"]),
                "failed": sum(1 for c in self.checks if not c["passed"]),
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=indent)


# ---------------------------------------------------------------------------
# R1 — Integridad de hashes
# ---------------------------------------------------------------------------

def _check_graph_hash(bundle: Dict) -> Tuple[bool, str]:
    """
    graph_hash = SHA256(evidence_graph SIN el campo graph_hash).
    El campo graph_hash es el resultado — no puede ser input de si mismo.
    """
    graph = bundle.get("evidence_graph", {})
    stored = bundle.get("integrity", {}).get("graph_hash", "")
    if not stored:
        return False, "graph_hash ausente en integrity"
    graph_for_hash = {k: v for k, v in graph.items() if k != "graph_hash"}
    recomputed = _sha256_dict(graph_for_hash)
    if recomputed != stored:
        return False, f"graph_hash NO coincide: recomputed={recomputed[:16]}... stored={stored[:16]}..."
    return True, "graph_hash integro"


def _check_policy_hash(bundle: Dict) -> Tuple[bool, str]:
    policy = bundle.get("policy_spec", {})
    stored = bundle.get("integrity", {}).get("policy_hash", "")
    if not stored:
        return False, "policy_hash ausente en integrity"
    recomputed = _sha256_dict(policy)
    if recomputed != stored:
        return False, f"policy_hash NO coincide: {recomputed[:16]}... != {stored[:16]}..."
    return True, "policy_hash integro"


def _check_bundle_hash(bundle: Dict) -> Tuple[bool, str]:
    """
    bundle_hash = SHA256(todo el contenido incluyendo evidence_graph con graph_hash asignado).
    Cualquier modificacion de cualquier campo invalida el bundle.
    """
    payload = {k: v for k, v in bundle.items() if k != "integrity"}
    recomputed = _sha256_dict(payload)
    stored = bundle.get("integrity", {}).get("bundle_hash", "")
    if not stored:
        return False, "bundle_hash ausente en integrity"
    if recomputed != stored:
        return False, f"bundle_hash NO coincide — bundle modificado o corrompido"
    return True, "bundle_hash integro"


# ---------------------------------------------------------------------------
# Level 1 — Estructura
# ---------------------------------------------------------------------------

def _check_structure(bundle: Dict) -> Tuple[bool, str]:
    required = [
        "bundle_version", "timestamp", "evidence_graph",
        "decision_trace", "policy_spec", "actions",
        "system_state", "integrity",
    ]
    missing = [f for f in required if f not in bundle]
    if missing:
        return False, f"Campos faltantes: {', '.join(missing)}"

    if bundle.get("bundle_version") not in _EBS_SUPPORTED_VERSIONS:
        return False, f"Version no soportada: {bundle.get('bundle_version')}"

    integrity = bundle.get("integrity", {})
    for h in ["bundle_hash", "graph_hash", "policy_hash"]:
        if h not in integrity:
            return False, f"Falta {h} en integrity"

    dt = bundle.get("decision_trace", {})
    for f in ["decision", "posterior", "risk"]:
        if f not in dt:
            return False, f"Falta {f} en decision_trace"

    if dt.get("decision") not in ("ACCEPT", "REJECT", "ABSTAIN"):
        return False, f"decision invalida: {dt.get('decision')}"

    return True, "Estructura EBS v1 valida"


# ---------------------------------------------------------------------------
# R2 — Cumplimiento de politica
# ---------------------------------------------------------------------------

def _check_policy_compliance(bundle: Dict) -> Tuple[bool, str, List[str]]:
    rules = {
        r["variable"]: r
        for r in bundle.get("policy_spec", {}).get("rules", [])
    }
    actions = bundle.get("actions", [])
    violations = []

    for i, action in enumerate(actions):
        var = action.get("variable", "")
        delta = abs(action.get("delta", 0.0))
        actor = action.get("actor", "system")

        if var not in rules:
            violations.append(f"Accion #{i}: variable '{var}' sin regla de politica")
            continue

        rule = rules[var]
        if delta > rule.get("max_delta", float("inf")):
            violations.append(
                f"Accion #{i}: |delta|={delta:.4f} > max_delta={rule['max_delta']:.4f} para '{var}'"
            )
        allowed = rule.get("allowed_roles", [])
        if allowed and actor not in allowed:
            violations.append(
                f"Accion #{i}: actor='{actor}' no autorizado para '{var}'"
            )

    if violations:
        return False, f"{len(violations)} violacion(es) de politica", violations
    return True, "Todas las acciones respetan la politica", []


# ---------------------------------------------------------------------------
# R3 — Coherencia de decision
# ---------------------------------------------------------------------------

def _check_decision_coherence(bundle: Dict) -> Tuple[bool, str]:
    dt = bundle.get("decision_trace", {})
    decision = dt.get("decision", "")
    risk = float(dt.get("risk", 0.0))
    posterior = float(dt.get("posterior", 0.5))
    epsilon = float(dt.get("epsilon_used", 0.05))

    if risk <= epsilon:
        expected = "ACCEPT"
    elif risk >= (1.0 - epsilon):
        expected = "REJECT"
    else:
        expected = "ABSTAIN"

    TOL = 1e-4
    if abs(risk - epsilon) < TOL or abs(risk - (1.0 - epsilon)) < TOL:
        return True, f"Decision en zona limite (tolerancia numerica aplicada)"

    if decision != expected:
        return (
            False,
            f"Incoherencia: risk={risk:.6f} epsilon={epsilon:.4f} "
            f"esperado={expected} almacenado={decision}",
        )

    # Validar rangos
    if not (0.0 <= posterior <= 1.0):
        return False, f"posterior={posterior} fuera de [0,1]"
    if risk < 0.0:
        return False, f"risk={risk} negativo"

    return True, f"Coherencia OK: decision={decision} risk={risk:.6f} epsilon={epsilon:.4f}"


# ---------------------------------------------------------------------------
# R4 — Engine attestation
# ---------------------------------------------------------------------------

def _check_engine_attestation(bundle: Dict) -> Tuple[bool, str]:
    att = bundle.get("integrity", {}).get("engine_attestation_hash", "")
    if not att:
        return False, "engine_attestation_hash ausente — Level 3 no alcanzable"
    if len(att) != 64 or not all(c in "0123456789abcdef" for c in att.lower()):
        return False, f"engine_attestation_hash formato invalido"
    return True, f"engine_attestation_hash presente: {att[:16]}..."


# ---------------------------------------------------------------------------
# R5 — ECL binding
# ---------------------------------------------------------------------------

def _check_ecl_binding(bundle: Dict) -> Tuple[bool, str]:
    ecl = bundle.get("integrity", {}).get("ecl_hash", "")
    if not ecl:
        return False, "ecl_hash ausente — sin anclaje ECL (Level 3 no alcanzable)"
    if len(ecl) != 64:
        return False, f"ecl_hash formato invalido"
    return True, f"ECL anclado: {ecl[:16]}..."


# ---------------------------------------------------------------------------
# Motor principal
# ---------------------------------------------------------------------------

def verify_bundle(
    bundle: Dict,
    strict: bool = False,
    verbose: bool = False,
) -> VerificationResult:

    result = VerificationResult()

    # Level 1: estructura
    ok, msg = _check_structure(bundle)
    result.add("L1_STRUCTURE", ok, msg, severity="ERROR" if not ok else "INFO")
    if not ok:
        result.conformity_level = 0
        result.passed = False
        return result

    result.conformity_level = 1

    # R3: coherencia de decision (no depende de hashes)
    ok, msg = _check_decision_coherence(bundle)
    result.add("R3_DECISION_COHERENCE", ok, msg, severity="ERROR" if not ok else "INFO")

    # R1: integridad criptografica
    ok_g, msg_g = _check_graph_hash(bundle)
    result.add("R1_GRAPH_HASH", ok_g, msg_g, severity="ERROR" if not ok_g else "INFO")

    ok_p, msg_p = _check_policy_hash(bundle)
    result.add("R1_POLICY_HASH", ok_p, msg_p, severity="ERROR" if not ok_p else "INFO")

    ok_b, msg_b = _check_bundle_hash(bundle)
    result.add("R1_BUNDLE_HASH", ok_b, msg_b, severity="ERROR" if not ok_b else "INFO")

    hash_ok = ok_g and ok_p and ok_b

    # R2: cumplimiento de politica
    ok_pc, msg_pc, violations = _check_policy_compliance(bundle)
    result.add(
        "R2_POLICY_COMPLIANCE", ok_pc, msg_pc,
        severity="ERROR" if not ok_pc else "INFO",
        detail=violations if violations and verbose else None,
    )

    # Determinar Level 2
    critical = result.critical_failures()
    if not critical and hash_ok and ok_pc:
        result.conformity_level = 2

    # R4 y R5 — solo WARNING, no bloquean Level 2
    ok_att, msg_att = _check_engine_attestation(bundle)
    result.add("R4_ENGINE_ATTESTATION", ok_att, msg_att, severity="WARNING" if not ok_att else "INFO")

    ok_ecl, msg_ecl = _check_ecl_binding(bundle)
    result.add("R5_ECL_BINDING", ok_ecl, msg_ecl, severity="WARNING" if not ok_ecl else "INFO")

    # Determinar Level 3
    if not critical and hash_ok and ok_pc and ok_att and ok_ecl:
        result.conformity_level = 3

    # Resultado final
    if result.conformity_level >= 2:
        result.passed = True
    elif strict:
        result.passed = False
    else:
        result.passed = result.conformity_level >= 1 and not critical

    if strict and result.conformity_level < 3:
        result.passed = False

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_result(result: VerificationResult, verbose: bool, as_json: bool) -> None:
    if as_json:
        print(result.to_json())
        return

    d = result.to_dict()
    status = "PASS" if result.passed else "FAIL"
    print(f"\n{'='*60}")
    print(f"  VIGIA — Verificador Independiente EBS v1  v{_VERIFIER_VERSION}")
    print(f"{'='*60}")
    print(f"  Resultado   : {status}")
    print(f"  Conformidad : Level {result.conformity_level} — {d['conformity_label']}")
    print(f"  Timestamp   : {result.timestamp}")
    s = d["summary"]
    print(f"  Checks      : {s['passed']}/{s['total']} OK")
    print(f"{'='*60}")

    if verbose or not result.passed:
        print()
        for check in result.checks:
            icon = "OK  " if check["passed"] else ("FAIL" if check["severity"] == "ERROR" else "WARN")
            print(f"  [{icon}] {check['rule']}")
            print(f"          {check['message']}")
            if check.get("detail") and verbose:
                for v in (check["detail"] if isinstance(check["detail"], list) else [check["detail"]]):
                    print(f"          > {v}")

    if not result.passed:
        print("\n  FALLAS CRITICAS:")
        for fail in result.critical_failures():
            print(f"    - {fail['rule']}: {fail['message']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verificador Independiente EBS v1 — VIGIA (stdlib puro)",
        epilog="Exit: 0=PASS  1=FAIL",
    )
    parser.add_argument("bundle_path", help="Ruta al bundle.json EBS v1")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--strict", "-s", action="store_true", help="Exige Level 3")
    parser.add_argument("--json", action="store_true", help="Salida JSON")

    args = parser.parse_args()

    try:
        with open(args.bundle_path, "r", encoding="utf-8") as f:
            bundle = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No encontrado: {args.bundle_path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON invalido: {e}", file=sys.stderr)
        return 1

    result = verify_bundle(bundle, strict=args.strict, verbose=args.verbose)
    _print_result(result, verbose=args.verbose, as_json=args.json)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
