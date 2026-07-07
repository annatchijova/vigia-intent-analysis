"""
vigia/core/canonicalize.py
===========================
Fuente de verdad única para _canonicalize en VIGÍA.

INVARIANTE: Este módulo define el esquema canónico de serialización para
hashing SHA-256. Todos los módulos que necesiten canonicalizar deben importar
desde aquí — excepto los verificadores stdlib-only (verify_ebs_v1.py y copias)
que mantienen su propia copia por diseño, EN LOCKSTEP (test_canonicalize_
lockstep.py lo verifica para v2 y para el fallback v1).

Esquema v2 (DEFAULT — sellos nuevos; R3-2, docs/REDTEAM_ROUND3_EMERGENT.md):
  bool     → "true" / "false"
  int      → "N:int"
  float    → "N.NNNNNNNN" (8 decimales fijos)
  str      → "s:" + NFC(CRLF/CR->LF)   ← escapado + normalizado
  None     → "null"
  Fraction → "num/den:frac"
  dict     → keys ordenadas, valores recursivos
  list     → elementos recursivos

Esquema v1 (LEGACY — solo verificación de bundles historicos): idéntico a v2
salvo `str → sin cambios` y `Fraction → str()`. Esa causa raíz producía
colisiones de tipo (True/"true", 1/"1:int", None/"null") e inestabilidad
(NFC/NFD, CRLF/LF → dos hashes). v2 lo cierra sin tocar la codificación de
escalares, así que la verificación prueba v2 y CAE A v1: todo bundle sellado
bajo v1 sigue verificando idéntico (results/), y los nuevos obtienen la
codificación sin colisiones.

Nota: execution_logger, compare_runs, evaluate_detector y run_pipeline NO
están en el camino de bundle sellado — usan la forma canónica como
representación/salida local, así que se fijan a v1 (comportamiento previo).
El fix v2 aplica al tamper-evidence de bundles sellados (bundle_builder /
hash_chain / verificadores).

CANONICALIZE_VERSION = "2" — default para sellos nuevos; v1 se conserva para
verificar bundles historicos.

signed-zero clarification (D3): the canonical form of every float zero
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

import unicodedata
from fractions import Fraction

# v2 (R3-2, docs/REDTEAM_ROUND3_EMERGENT.md) es el esquema DEFAULT para sellos
# nuevos. v1 se conserva para verificar bundles historicos (todos los de
# results/ se sellaron bajo v1). Los verificadores prueban v2 y caen a v1.
CANONICALIZE_VERSION: str = "2"

# Prefijo univoco para strings — impide que "true"/"1:int"/"null" colisionen
# con el tag de un escalar (True/1/None). Cualquier prefijo funciona mientras
# NO pueda ser producido por la codificacion de un escalar; "s:" no lo es.
_V2_STR_PREFIX: str = "s:"


def _v2_norm_str(s: str) -> str:
    """Normaliza un string para hashing v2: line endings CRLF/CR -> LF, luego
    NFC. Cierra la inestabilidad "un mismo string logico -> dos hashes"
    (NFC/NFD, CRLF/LF)."""
    return unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n"))


def _canonicalize_v1(obj: Any) -> Any:
    """
    Esquema v1 (LEGACY — congelado). Solo para verificar bundles historicos.

    Reglas:
    - bool  → "true" / "false"  (antes de int — bool es subclase de int)
    - int   → "N:int"
    - float → "N.NNNNNNNN" (8 decimales), "nan", "inf", "-inf"
    - str   → sin cambios   ← causa raiz de las colisiones R3-2
    - None  → "null"
    - dict  → keys ordenadas, valores recursivos
    - list/tuple → elementos recursivos
    - otros → str() — fallback

    DEBILIDAD (R3-2): strings sin escapar colisionan con tags de escalar, y
    NFC/NFD + CRLF/LF producen dos hashes para un mismo string. Corregido en v2.
    NO usar para sellos nuevos.
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
        return {k: _canonicalize_v1(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v1(v) for v in obj]
    return str(obj)


def _canonicalize_v2(obj: Any) -> Any:
    """
    Esquema v2 (R3-2) — DEFAULT para sellos nuevos. Cierra las colisiones.

    Diferencias con v1 (ESCALARES IDENTICOS — solo cambian strings y Fraction):
    - str      → "s:" + NFC(CRLF/CR->LF)   [prefijo univoco + normalizacion]
    - Fraction → "num/den:frac"            [antes caia a str() -> "1/2"]
    - fallback → "s:" + NFC(str(obj))      [nunca crudo, evita colision]
    - bool/int/float/None/dict/list        [identicos a v1, bit a bit]

    Por que esto cierra las 3 clases del hallazgo:
    - True->"true" vs "true"->"s:true"       : ya no colisionan.
    - 1->"1:int"  vs "1:int"->"s:1:int"      : ya no colisionan.
    - None->"null" vs "null"->"s:null"       : ya no colisionan.
    - NFC/NFD y CRLF/LF                       : normalizados a una sola forma.
    - Fraction(1,2)                           : univoco y estable.
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
        return _V2_STR_PREFIX + _v2_norm_str(obj)
    if obj is None:
        return "null"
    if isinstance(obj, Fraction):
        return f"{obj.numerator}/{obj.denominator}:frac"
    if isinstance(obj, dict):
        return {k: _canonicalize_v2(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize_v2(v) for v in obj]
    return _V2_STR_PREFIX + _v2_norm_str(str(obj))


# Default para todo el codigo de produccion (sellado nuevo) = v2.
def _canonicalize(obj: Any) -> Any:
    """Forma canonica DEFAULT (v2). Ver _canonicalize_v2."""
    return _canonicalize_v2(obj)
