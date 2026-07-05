"""
vigia/core/canonicalize.py
===========================
Fuente de verdad única para _canonicalize en VIGÍA.

INVARIANTE: Este módulo define el esquema canónico v1 de serialización
para hashing SHA-256. Todos los módulos que necesiten canonicalizar
deben importar desde aquí — excepto los verificadores stdlib-only
(verify_ebs_v1.py y copias) que mantienen su propia copia por diseño.

Esquema v1 (compatible con bundle_builder.py y verify_ebs_v1.py):
  bool  → "true" / "false"
  int   → "N:int"
  float → "N.NNNNNNNN" (8 decimales fijos)
  str   → sin cambios
  None  → "null"
  dict  → keys ordenadas, valores recursivos
  list  → elementos recursivos

Nota: execution_logger, compare_runs, evaluate_detector y run_pipeline
usaban esquemas divergentes (bool → "true:bool", str → "str:X").
Esta unificación garantiza que el mismo input produce el mismo hash
en cualquier módulo — requisito Daubert de reproducibilidad.

CANONICALIZE_VERSION = "1" — incluir en bundles para trazabilidad.
Cuando se migre al esquema v2 (prefijos "tipo::"), incrementar este valor
y mantener soporte de verificación para v1.

v1 clarification (signed zero, D3): the canonical form of every float zero
is "0.00000000" — IEEE-754 negative zero (-0.0) is normalized before
formatting ("obj + 0.0"). This is not a schema change: -0.0 == 0.0 are the
same number, and no historically sealed bundle contains -0.0 (verified
against results/), so every previously emitted hash still verifies
identically. Every copy of the encoder (bundle_builder, the stdlib-only
verifiers, verify_tool_log, the chain_of_custody fallback) applies the same
rule in lockstep.
"""
from __future__ import annotations

from typing import Any

CANONICALIZE_VERSION: str = "1"


def _canonicalize(obj: Any) -> Any:
    """
    Convierte recursivamente un objeto a forma canónica estricta para hasheo.

    Reglas:
    - bool  → "true" / "false"  (antes de int — bool es subclase de int)
    - int   → "N:int"
    - float → "N.NNNNNNNN" (8 decimales), "nan", "inf", "-inf"
    - str   → sin cambios
    - None  → "null"
    - dict  → keys ordenadas, valores recursivos
    - list/tuple → elementos recursivos
    - otros → str() — fallback, no rompe el hash
    """
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
        return {k: _canonicalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]
    return str(obj)
