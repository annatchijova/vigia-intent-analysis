"""
vigia/tools/adversarial_mutation_suite.py

Suite de Mutaciones Adversariales — VIGÍA P2
============================================

Genera vectores de prueba adversariales para validar la robustez del
pipeline contra ataques de perturbación de input.

INSPIRACIÓN Y CRÉDITO:
    Las familias de transformación implementadas aquí (ruido Unicode de
    baja tasa, inflación de espacio de símbolos, estructura falsa,
    explotación de tie-break, aliasing LZ) están conceptualmente inspiradas
    en el trabajo de mutación adversarial de:

        Soedov, M. (2024). Agentic Security: Red Teaming Framework for
        Large Language Models. GitHub repository.
        https://github.com/msoedov/agentic_security

    El código es implementación original de VIGÍA, escrito desde cero
    para operar sobre artefactos forenses (no sobre prompts LLM) y
    para mapear explícitamente a los GAPs adversariales documentados
    en P2_SPEC §14.

FILOSOFÍA:
    Estos vectores NO son ataques al sistema — son instrumentos de
    auditoría. El objetivo es verificar que el pipeline detecta la
    perturbación, la documenta en el bundle, y NO produce resultados
    silenciosamente incorrectos.

    "Si el sistema no puede detectar su propia perturbación,
     no puede ser admitido como evidencia forense." — VIGÍA P2_SPEC

MAPEO GAP → FAMILIA DE MUTACIÓN:
    GAP-01  entropy_inflation_attack   → NoiseInjectionMutator
    GAP-02  symbolic_explosion_attack  → SymbolExplosionMutator
    GAP-06  false_structure_induction  → FalseStructureMutator
    GAP-09  tie_break_exploitation     → TieBreakMutator
    GAP-10  lz_period_aliasing         → PeriodAliasingMutator

INVARIANTE DE SEGURIDAD:
    Ninguna mutación modifica el artefacto original en memoria.
    Todas las funciones son puras — reciben string/bytes, retornan
    string/bytes nuevo. El bundle_hash del artefacto original no
    puede ser afectado por este módulo.

DETERMINISMO:
    Todas las transformaciones que usan pseudo-aleatoriedad aceptan
    un parámetro `seed: int` obligatorio. Sin seed explícito, el
    módulo lanza ValueError — nunca produce resultados no reproducibles
    en silencio.

NORMALIZACIÓN — CORRECCIÓN P0 (hallazgo DeepSeek, auditado 2026-05-18):
    NFKC NO neutraliza todos los vectores de este módulo. Verificado
    empíricamente contra CPython 3.12 + Unicode 15.1:

    - ZERO WIDTH SPACE (U+200B), ZWNJ (U+200C), ZWJ (U+200D):
      categoría Unicode Cf (format character). NFKC los preserva intactos.
      Neutralización correcta: strip por categoría Cf/Cc/Cs.

    - Homoglifos cirílicos (U+0430 а, U+0435 е, U+043E о, etc.):
      categoría Ll (lowercase letter). NFKC los preserva intactos.
      casefold() tampoco los normaliza.
      Neutralización correcta: confusable mapping explícito
      (Unicode TR#39 confusables.txt).

    Este módulo expone 3 funciones de normalización especializadas:
      normalize_for_entropy()           — 4 capas, para métricas de entropía
      normalize_for_indexing()          — NFKC + control_strip, preserva case
      normalize_for_visual_equivalence()— NFKC + confusable + control_strip

    No hay una función normalize_for_analysis() totalizante — destruiría
    información necesaria para evidencia original y atribución.
    El pipeline decide qué función aplicar según el propósito.

    El perfil de normalización activo se expone en NORMALIZATION_PROFILE
    (incluye unicode_version) para detectar divergencia cross-platform.

LIMITACIONES CONOCIDAS (roadmap v2.1):
    - _lcg() es un LCG de Knuth. NO es criptográficamente seguro.
      No usar para generación de secretos, claves, ni nonces.
      Propósito exclusivo: reproducibilidad determinista de vectores de test.

    - SymbolExplosionMutator v1.0 cubre homoglifos cirílicos/griegos básicos.
      Roadmap v2.1: NFC/NFD decomposition, bidi override (U+202E),
      mixed-script identifiers, UTF-8 overlong encoding.

    - FalseStructureMutator v1.0 modela solo repetición periódica simple.
      GAP-06 real incluye: estructura tipo gramática, Markov-consistent nonsense.
      La implementación actual es un subconjunto de GAP-06.

    - TieBreakMutator v1.0 usa homogeneización uniforme.
      Roadmap v2.1: ventanas deslizantes patológicas, secuencias constantes
      con spikes, aliasing temporal.

    - Determinismo cross-platform depende de la versión de Unicode del
      intérprete Python. Testeado en Linux (CPython 3.12, Unicode 15.1).
      Pendiente: macOS, Windows. La versión Unicode DEBE congelarse en el
      spec si se requiere reproducibilidad cross-platform estricta.

    Crédito de auditoría: hallazgos P0 y roadmap identificados por
    DeepSeek (auditoría colectiva VIGÍA, 2026-05-18).

Licencia: Apache 2.0
Repositorio: https://github.com/annatchijova/vigia-intent-analysis
Autora principal: Anna Tchijova — VIGÍA Collective
Auditoría colectiva: Kimi/Moonshot, DeepSeek, Gemini, Qwen, ChatGPT
Versión: 1.2 — 19 de mayo de 2026
Audiencia: SANS FIND EVIL Hackathon 2026 / SIFT Workstation

HISTORIAL DE PATCHES:
    B5+B6  : orden confusable→casefold corregido, minúsculas griegas al mapa
    Fix 5  : TieBreakMutator — rejection sampling determinista
    Fix 6  : FalseStructureMutator — modelo bigram determinista
    Fix 7  : MutationResult — mutation_id determinista (SHA-256)
    P5     : PeriodAliasingMutator — sqrt_n y aliasing_zone en bundle
             usan _dround() P0, no round() nativo — Kimi 2026-05-19

LIMITACIONES CONOCIDAS:
    - _lcg() es un LCG de Knuth. NO es criptográficamente seguro.
      No usar para generación de secretos, claves, ni nonces.
      Propósito exclusivo: reproducibilidad determinista de vectores de test.
    - SymbolExplosionMutator v1.0 cubre homoglifos cirílicos/griegos básicos.
      Roadmap v2.1: NFC/NFD decomposition, bidi override (U+202E),
      mixed-script identifiers, UTF-8 overlong encoding.
    - FalseStructureMutator v1.0 modela solo repetición periódica simple
      (bigram orden-1). GAP-06 completo incluye Markov orden-k y gramáticas
      context-free. La implementación actual es un subconjunto de GAP-06.
    - TieBreakMutator v1.0 usa homogeneización uniforme.
      Roadmap v2.1: ventanas deslizantes patológicas, secuencias constantes
      con spikes, aliasing temporal.
    - Determinismo cross-platform depende de la versión Unicode del intérprete.
      Testeado en Linux CPython 3.12, Unicode 15.1.
      Pendiente: macOS, Windows. La versión Unicode debe congelarse en el
      spec si se requiere reproducibilidad cross-platform estricta.
      NORMALIZATION_PROFILE expone unicode_version para detectar divergencia.
    - int(n ** 0.5) en PeriodAliasingMutator usa float nativo — correcto para
      aritmética de período (entero), no afecta campos de output forense.
"""

from __future__ import annotations

import decimal
import hashlib
import json
import math
import unicodedata
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# P5: Determinismo P0 — definición local, misma semántica que vigia_scorer.py
# Este módulo no importa de vigia_scorer para mantenerse standalone.
# Los campos numéricos que van al bundle forense usan _dround para garantizar
# output bit-identical en x86-64 y ARM64.
# ---------------------------------------------------------------------------
decimal.getcontext().prec     = 28
decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN

_DETERMINISTIC_OUTPUT_PREC = 4


def _dround(value, precision: int = _DETERMINISTIC_OUTPUT_PREC) -> float:
    """
    Redondeo determinístico P0.
    Finite Math Shield: retorna 0.0 para inf, -inf, NaN.
    Solo para campos numéricos que van al bundle forense.
    NO usar para el LCG ni para aritmética interna de mutación.
    """
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

VERSION = "1.1"
MODULE_NAME = "ADV_MUTATION_SUITE"

# Familias de mutación y sus GAPs asociados
GAP_MAP: Dict[str, List[str]] = {
    "NoiseInjectionMutator":   ["GAP-01"],
    "SymbolExplosionMutator":  ["GAP-02"],
    "FalseStructureMutator":   ["GAP-06"],
    "TieBreakMutator":         ["GAP-09"],
    "PeriodAliasingMutator":   ["GAP-10"],
}


# ---------------------------------------------------------------------------
# Normalización en 4 capas — corrección P0 (DeepSeek, 2026-05-18)
# NFKC sola NO es suficiente para neutralizar los vectores de este módulo.
# ---------------------------------------------------------------------------

# Confusable mapping Unicode TR#39 — subconjunto forense relevante
# Fuente: https://www.unicode.org/reports/tr39/#Confusable_Detection
# Esta lista cubre los homoglifos usados en SymbolExplosionMutator v1.0.
#
# B5+B6 fix (auditoría Doc5, 2026-05-18):
# El mapa original solo tenía MAYÚSCULAS griegas (Α Ε Ο Β).
# casefold() las convierte a minúsculas ANTES del mapeo → α ε ο β no estaban en el mapa
# → homoglifos griegos pasaban intactos a través de normalize_for_entropy.
# Solución doble: agregar minúsculas griegas AL mapa Y corregir el orden de capas
# en normalize_for_entropy (confusable ANTES de casefold).
#
# Roadmap v2.1: cargar desde confusables.txt completo para cobertura total.
_CONFUSABLE_MAP: Dict[str, str] = {
    # Cirílico → latino (mayúsculas y minúsculas)
    "\u0430": "a",   # а cirílico → a latino
    "\u0410": "A",   # А cirílico → A latino
    "\u0435": "e",   # е cirílico → e latino
    "\u0415": "E",   # Е cirílico → E latino
    "\u043e": "o",   # о cirílico → o latino
    "\u041e": "O",   # О cirílico → O latino
    "\u0440": "p",   # р cirílico → p latino
    "\u0420": "P",   # Р cirílico → P latino
    "\u0441": "c",   # с cirílico → c latino
    "\u0421": "C",   # С cirílico → C latino
    "\u0445": "x",   # х cirílico → x latino
    "\u0425": "X",   # Х cirílico → X latino
    # Griego → latino (MAYÚSCULAS — antes de casefold en normalize_for_entropy)
    "\u0391": "A",   # Α griego  → A latino
    "\u0395": "E",   # Ε griego  → E latino
    "\u039f": "O",   # Ο griego  → O latino
    "\u0392": "B",   # Β griego  → B latino
    # Griego → latino (minúsculas — necesario para normalize_for_visual_equivalence
    # donde casefold no se aplica, y como fallback en normalize_for_entropy)
    "\u03b1": "a",   # α griego  → a latino
    "\u03b5": "e",   # ε griego  → e latino
    "\u03bf": "o",   # ο griego  → o latino
    "\u03b2": "b",   # β griego  → b latino
    "\u03c1": "p",   # ρ griego  → p latino
    "\u03c2": "c",   # ς griego  → c latino (sigma final)
    "\u03c7": "x",   # χ griego  → x latino
}

# Categorías Unicode que deben eliminarse en análisis forense
# Cf = format characters (zero-width, bidi marks, etc.)
# Cc = control characters
# Cs = surrogate characters
_STRIP_CATEGORIES = frozenset({"Cf", "Cc", "Cs"})


# ---------------------------------------------------------------------------
# Perfil de normalización — provenance forense (Fix 4)
# Embeber en reports y bundles para detectar divergencia cross-platform.
# ---------------------------------------------------------------------------

import unicodedata as _ud_version_check  # noqa: E402

NORMALIZATION_PROFILE: Dict[str, str] = {
    "unicode_version":  _ud_version_check.unidata_version,
    "python_version":   __import__("sys").version.split()[0],
    "profile_id":       "vigia_nfkc_cf_tr39_v1",
    "module_version":   VERSION,
    "confusable_set":   "vigia_cyrillic_greek_basic_v1",
    "strip_categories": "Cf,Cc,Cs",
    "warning": (
        "Normalización cross-platform: mismos hashes pre-normalización "
        "pueden producir hashes post-normalización distintos si la versión "
        "de Unicode del intérprete difiere. Verificar unicode_version al "
        "comparar bundles entre máquinas."
    ),
}


# ---------------------------------------------------------------------------
# Normalización en 3 funciones especializadas — Fix 3
# Una función totalizante destruye información necesaria para evidencia
# original. Separar por propósito: indexing != entropy != visual equivalence.
# ---------------------------------------------------------------------------

def normalize_for_entropy(text: str) -> str:
    """
    Normalización para cálculo de entropía y complejidad (LZ, PE, Markov).

    Aplica las 4 capas: NFKC + casefold + confusable_map + control_strip.
    Destruye información de capitalización y collapsa homoglifos.

    USO CORRECTO: como pre-procesamiento antes de tokenizar para métricas
    de entropía. El resultado NO debe usarse como representación de la
    evidencia original — es una forma canónica de análisis.

    B5 fix (auditoría Doc5, 2026-05-18):
    Orden corregido: confusable_map ANTES de casefold.
    El orden anterior era NFKC→casefold→confusable, lo que hacía que casefold
    convirtiera Α→α (griego mayúscula→minúscula) ANTES del mapeo, y α no estaba
    en el mapa → homoglifos griegos pasaban intactos.
    Orden correcto: NFKC→confusable→casefold→control_strip.
    """
    result = unicodedata.normalize("NFKC", text)
    # Capa 2: confusable_map PRIMERO — antes de casefold para capturar mayúsculas
    result = "".join(_CONFUSABLE_MAP.get(ch, ch) for ch in result)
    # Capa 3: casefold — después del mapeo
    result = result.casefold()
    # Capa 4: control strip
    result = "".join(
        ch for ch in result
        if unicodedata.category(ch) not in _STRIP_CATEGORIES
    )
    return result


def normalize_for_indexing(text: str) -> str:
    """
    Normalización para indexación y búsqueda en corpus forense.

    Aplica solo NFKC + control_strip. Preserva capitalización y
    no collapsa homoglifos — la distinción entre 'Admin' y 'admin'
    puede ser evidencia forense relevante.

    USO CORRECTO: hash de artefactos para deduplicación, búsqueda
    en corpus, comparación de logs.
    """
    result = unicodedata.normalize("NFKC", text)
    result = "".join(
        ch for ch in result
        if unicodedata.category(ch) not in _STRIP_CATEGORIES
    )
    return result


def normalize_for_visual_equivalence(text: str) -> str:
    """
    Normalización para detectar equivalencia visual (homoglifo detection).

    Aplica NFKC + confusable_map + control_strip. NO aplica casefold —
    preserva la distinción de capitalización para que 'Admin' y 'ADMIN'
    sean distinguibles, pero 'аdmin' (cirílico) y 'admin' (latino) sean
    equivalentes.

    USO CORRECTO: verificar si dos strings son visualmente indistinguibles
    para un humano (vector de GAP-02). Detectar homoglifo attacks en
    nombres de usuario, dominios, comandos.
    """
    result = unicodedata.normalize("NFKC", text)
    result = "".join(_CONFUSABLE_MAP.get(ch, ch) for ch in result)
    result = "".join(
        ch for ch in result
        if unicodedata.category(ch) not in _STRIP_CATEGORIES
    )
    return result


# ---------------------------------------------------------------------------
# Utilidades deterministas (sin random implícito)
# ---------------------------------------------------------------------------

def _lcg(seed: int, count: int) -> List[int]:
    """
    Generador congruencial lineal determinista.
    Parámetros clásicos de Knuth (TAOCP Vol.2).
    Produce `count` enteros en [0, 2^32).

    No usa random.* ni numpy — garantía de reproducibilidad cross-platform.

    ADVERTENCIA DE SEGURIDAD (hallazgo DeepSeek P0, 2026-05-18):
    NO es criptográficamente seguro. No usar para generación de secretos,
    claves, nonces, tokens ni ningún contexto que requiera impredecibilidad.
    Propósito exclusivo: reproducibilidad determinista de vectores de test.
    Para uso criptográfico usar secrets o os.urandom().
    """
    a = 1664525
    c = 1013904223
    m = 2 ** 32
    state = seed & 0xFFFFFFFF
    results = []
    for _ in range(count):
        state = (a * state + c) % m
        results.append(state)
    return results


def _nfkc(text: str) -> str:
    """Normalización NFKC — misma que aplica el pipeline principal."""
    return unicodedata.normalize("NFKC", text)


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8", errors="replace")).hexdigest()


# ---------------------------------------------------------------------------
# Resultado de mutación
# ---------------------------------------------------------------------------

class MutationResult:
    """
    Resultado de una mutación adversarial.

    Attributes:
        mutation_id     : SHA-256 determinista de (mutator_name + original_hash
                          + canonical_json(params)). Identifica unívocamente
                          este vector para trazabilidad en bundles y auditorías.
        mutator_name    : nombre de la familia de mutación
        gap_ids         : GAPs P2 que este vector ejerce
        original_hash   : SHA-256 del artefacto original (pre-mutación)
        mutated_hash    : SHA-256 del artefacto mutado
        mutation_params : parámetros exactos usados (para reproducibilidad)
        mutated_text    : texto mutado
        intensity       : Fraction — intensidad de la perturbación [0, 1]
        description     : descripción humano-legible del vector
    """

    __slots__ = (
        "mutation_id", "mutator_name", "gap_ids", "original_hash", "mutated_hash",
        "mutation_params", "mutated_text", "intensity", "description",
    )

    def __init__(
        self,
        mutator_name: str,
        gap_ids: List[str],
        original_text: str,
        mutated_text: str,
        mutation_params: Dict[str, Any],
        intensity: Fraction,
        description: str,
    ) -> None:
        self.mutator_name = mutator_name
        self.gap_ids = gap_ids
        self.original_hash = _sha256_hex(original_text)
        self.mutated_hash = _sha256_hex(mutated_text)
        self.mutated_text = mutated_text
        self.mutation_params = mutation_params
        self.intensity = intensity
        self.description = description
        # Fix 7: mutation_id determinista — sha256(mutator + original_hash + params)
        # Permite identificar unívocamente este vector en bundles y auditorías
        # sin necesidad de almacenar el texto completo.
        _params_canonical = json.dumps(
            mutation_params, sort_keys=True, ensure_ascii=True, default=str
        )
        self.mutation_id = _sha256_hex(
            mutator_name + "|" + self.original_hash + "|" + _params_canonical
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mutation_id":     self.mutation_id,
            "mutator_name":    self.mutator_name,
            "gap_ids":         self.gap_ids,
            "original_hash":   self.original_hash,
            "mutated_hash":    self.mutated_hash,
            "mutation_params": self.mutation_params,
            "intensity":       str(self.intensity),
            "description":     self.description,
            "hashes_differ":   self.original_hash != self.mutated_hash,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MutationResult({self.mutator_name}, "
            f"gaps={self.gap_ids}, "
            f"intensity={float(self.intensity):.3f}, "
            f"id={self.mutation_id[:12]}...)"
        )


# ---------------------------------------------------------------------------
# GAP-01 — NoiseInjectionMutator
# Inspiración conceptual: noise_injection en agentic_security (Soedov, 2024)
# ---------------------------------------------------------------------------

class NoiseInjectionMutator:
    """
    GAP-01: entropy_inflation_attack

    Inyecta caracteres Unicode de control de baja visibilidad en posiciones
    pseudo-aleatorias del texto. La semántica visible no cambia, pero el
    espacio de símbolos se expande y la entropía Shannon sube artificialmente.

    Un pipeline robusto DEBE:
    1. Detectar la diferencia de hash pre/post normalización NFKC.
    2. Reportar la inflación de entropía como señal sospechosa.
    3. Operar sobre el texto normalizado, no el mutado.

    Parámetro `rate`: fracción de caracteres originales que reciben ruido.
    Rate bajo (< 0.05) es el caso más peligroso — difícil de ver, efecto
    estadístico real.
    """

    NOISE_CHARS = [
        "\u200b",  # ZERO WIDTH SPACE
        "\u200c",  # ZERO WIDTH NON-JOINER
        "\u200d",  # ZERO WIDTH JOINER
        "\u2060",  # WORD JOINER
        "\ufeff",  # ZERO WIDTH NO-BREAK SPACE (BOM)
        "\u00ad",  # SOFT HYPHEN
    ]

    def mutate(
        self,
        text: str,
        rate: Fraction = Fraction(3, 100),
        seed: int = 42,
    ) -> MutationResult:
        """
        Inyecta ruido a tasa `rate`.

        Args:
            text : artefacto original (string plano)
            rate : proporción de posiciones ruidosas, en [0, 1/5]
            seed : semilla determinista obligatoria

        Raises:
            ValueError: si rate > 1/5 (sobre ese umbral el artefacto es
                        irreconocible, lo cual sale del alcance de GAP-01)
            ValueError: si text está vacío
        """
        if not text:
            raise ValueError("NoiseInjectionMutator: text no puede estar vacío")
        if rate > Fraction(1, 5):
            raise ValueError(
                f"NoiseInjectionMutator: rate={rate} excede 1/5. "
                "GAP-01 modela ruido de baja tasa. Para tasas altas usar SymbolExplosionMutator."
            )

        n = len(text)
        n_noise = int(n * float(rate))
        if n_noise == 0:
            # Rate tan bajo que no produce ninguna inserción — vector degenerado
            return MutationResult(
                mutator_name="NoiseInjectionMutator",
                gap_ids=["GAP-01"],
                original_text=text,
                mutated_text=text,
                mutation_params={"rate": str(rate), "seed": seed, "n_noise": 0},
                intensity=Fraction(0),
                description="Rate demasiado bajo para texto de esta longitud — vector degenerado",
            )

        rng = _lcg(seed, n_noise * 2)
        positions = sorted(set(r % (n + 1) for r in rng[:n_noise]))
        char_indices = [r % len(self.NOISE_CHARS) for r in rng[n_noise : n_noise + len(positions)]]

        chars = list(text)
        # Insertar de atrás para adelante para no desplazar índices
        for pos, ci in sorted(zip(positions, char_indices), reverse=True):
            chars.insert(pos, self.NOISE_CHARS[ci % len(self.NOISE_CHARS)])

        mutated = "".join(chars)
        intensity = Fraction(len(positions), max(n, 1))

        return MutationResult(
            mutator_name="NoiseInjectionMutator",
            gap_ids=["GAP-01"],
            original_text=text,
            mutated_text=mutated,
            mutation_params={
                "rate":          str(rate),
                "seed":          seed,
                "n_noise":       len(positions),
                "positions":     positions[:10],  # primeras 10 para trazabilidad
                "noise_chars":   [self.NOISE_CHARS[ci % len(self.NOISE_CHARS)] for ci in char_indices[:10]],
            },
            intensity=intensity,
            description=(
                f"Inyección de {len(positions)} caracteres Unicode invisibles "
                f"en {n} posiciones (rate={float(rate):.3f}). "
                f"Entropía Shannon se infla sin cambio semántico visible. "
                f"Normalización NFKC DEBE eliminar el ruido antes del análisis."
            ),
        )


# ---------------------------------------------------------------------------
# GAP-02 — SymbolExplosionMutator
# Inspiración conceptual: random_case, rot13, zigzag en agentic_security (Soedov, 2024)
# ---------------------------------------------------------------------------

class SymbolExplosionMutator:
    """
    GAP-02: symbolic_explosion_attack

    Aplica transformaciones de capitalización pseudo-aleatoria y
    substitución de caracteres visualmente similares (homoglifos).
    El significado semántico se preserva para el ojo humano, pero
    el espacio de símbolos del tokenizador se expande artificialmente,
    inflando la entropía Shannon del artefacto.

    Un pipeline robusto DEBE aplicar normalización antes de tokenizar.
    Si no lo hace, el engine de entropía ve 'A' y 'a' como símbolos
    distintos, y 'o' y 'ο' (omicron griego) como símbolos distintos.

    Esto es exactamente el vector que NFKC + casefold en `security.py`
    está diseñado para neutralizar.
    """

    # Homoglifos: (original, sustituto Unicode visualmente idéntico)
    HOMOGLYPHS: List[Tuple[str, str]] = [
        ("a", "\u0430"),   # а cirílico
        ("e", "\u0435"),   # е cirílico
        ("o", "\u043e"),   # о cirílico
        ("p", "\u0440"),   # р cirílico
        ("c", "\u0441"),   # с cirílico
        ("x", "\u0445"),   # х cirílico
        ("A", "\u0391"),   # Α griego
        ("E", "\u0395"),   # Ε griego
        ("O", "\u039f"),   # Ο griego
        ("B", "\u0392"),   # Β griego
    ]

    def mutate(
        self,
        text: str,
        homoglyph_rate: Fraction = Fraction(1, 10),
        case_rate: Fraction = Fraction(2, 10),
        seed: int = 42,
    ) -> MutationResult:
        """
        Combina substitución por homoglifos y alternancia de capitalización.

        Args:
            text           : artefacto original
            homoglyph_rate : fracción de caracteres elegibles para homoglifo
            case_rate      : fracción de caracteres elegibles para case flip
            seed           : semilla determinista obligatoria
        """
        if not text:
            raise ValueError("SymbolExplosionMutator: text no puede estar vacío")

        homoglyph_map = dict(self.HOMOGLYPHS)
        n = len(text)
        rng = _lcg(seed, n * 2)

        chars = list(text)
        homoglyph_count = 0
        case_count = 0

        for i, ch in enumerate(chars):
            r1 = Fraction(rng[i] % 1000, 1000)
            r2 = Fraction(rng[n + i] % 1000, 1000)

            if ch in homoglyph_map and r1 < homoglyph_rate:
                chars[i] = homoglyph_map[ch]
                homoglyph_count += 1
            elif ch.isalpha() and r2 < case_rate:
                chars[i] = ch.lower() if ch.isupper() else ch.upper()
                case_count += 1

        mutated = "".join(chars)
        total_modified = homoglyph_count + case_count
        intensity = Fraction(total_modified, max(n, 1))

        return MutationResult(
            mutator_name="SymbolExplosionMutator",
            gap_ids=["GAP-02"],
            original_text=text,
            mutated_text=mutated,
            mutation_params={
                "homoglyph_rate":  str(homoglyph_rate),
                "case_rate":       str(case_rate),
                "seed":            seed,
                "homoglyph_count": homoglyph_count,
                "case_count":      case_count,
            },
            intensity=intensity,
            description=(
                f"Substitución de {homoglyph_count} homoglifos cirílicos/griegos "
                f"+ {case_count} alternancias de capitalización. "
                f"El tokenizador sin normalización ve {total_modified} símbolos "
                f"adicionales distintos. Entropía Shannon se infla artificialmente."
            ),
        )


# ---------------------------------------------------------------------------
# GAP-06 — FalseStructureMutator
# ---------------------------------------------------------------------------

class FalseStructureMutator:
    """
    GAP-06: false_structure_induction

    Genera texto con estructura estadística superficialmente plausible
    (distribución bigram similar al original) pero sin coherencia semántica
    real. Un detector que usa solo LZ o entropía de primer orden puede
    clasificar este output como "normal" cuando es ruido estructurado.

    DIFERENCIA CON PeriodAliasingMutator:
        PeriodAliasingMutator ejerce GAP-10 — instabilidad matemática de
        la normalización asintótica LZ76 para períodos cerca de sqrt(n).
        Es un ataque a la precisión numérica del algoritmo.

        FalseStructureMutator ejerce GAP-06 — estructura semánticamente
        vacía que engaña a detectores de anomalías basados en distribución.
        Es un ataque a la validez estadística del modelo de normalidad.

    TÉCNICA (Fix 6, Anna Tchijova, 2026-05-18):
        Construye un modelo bigram determinista del texto original y genera
        texto de la misma longitud usando esos bigrams como transiciones.
        El resultado tiene distribución de bigrams similar al original
        (LZ moderado, entropía similar) pero es semánticamente incoherente.

        Esto modela el caso real donde un adversario genera logs sintéticos
        con frecuencias de caracteres calibradas para pasar filtros estadísticos.

    LIMITACIÓN v1.1 (documentada — roadmap v2.1):
        El modelo bigram captura memoria de orden 1. GAP-06 completo incluye
        Markov orden-k y gramáticas context-free. La implementación actual
        es un subconjunto del gap real.
    """

    def mutate(
        self,
        text: str,
        seed: int = 42,
    ) -> MutationResult:
        """
        Genera texto con distribución bigram similar al original pero
        semánticamente incoherente.

        Args:
            text : artefacto original (mínimo 4 caracteres para bigrams útiles)
            seed : semilla determinista
        """
        if not text:
            raise ValueError("FalseStructureMutator: text no puede estar vacío")
        if len(text) < 4:
            raise ValueError(
                "FalseStructureMutator: text demasiado corto (mínimo 4 chars "
                "para construir modelo bigram útil)"
            )

        n = len(text)

        # --- Construir tabla bigram determinista ---
        # bigrams[ch] = lista de caracteres que siguen a ch en el original
        bigrams: Dict[str, List[str]] = {}
        for i in range(len(text) - 1):
            ch = text[i]
            nxt = text[i + 1]
            bigrams.setdefault(ch, []).append(nxt)

        # Punto de inicio: determinista por seed
        rng = _lcg(seed, n + 1)
        start_idx = rng[0] % n
        current = text[start_idx]

        # --- Generar texto por caminata sobre el modelo bigram ---
        generated = [current]
        all_chars = list(set(text))  # universo de caracteres del artefacto

        for i in range(1, n):
            r = rng[i]
            successors = bigrams.get(current)
            if successors:
                # Elegir sucesor del modelo bigram (determinista)
                nxt = successors[r % len(successors)]
            else:
                # current no tiene sucesor conocido — fallback al universo
                nxt = all_chars[r % len(all_chars)]
            generated.append(nxt)
            current = nxt

        mutated = "".join(generated)

        return MutationResult(
            mutator_name="FalseStructureMutator",
            gap_ids=["GAP-06"],
            original_text=text,
            mutated_text=mutated,
            mutation_params={
                "seed":               seed,
                "technique":          "bigram_markov_order1",
                "n_unique_chars":     len(all_chars),
                "n_bigram_states":    len(bigrams),
                "start_char":         text[start_idx],
                "start_idx":          int(start_idx),
                "limitation":         "Markov order-1 subset of GAP-06. Roadmap v2.1: order-k.",
            },
            intensity=Fraction(1, 1),
            description=(
                f"Texto generado por caminata bigram sobre el modelo estadístico "
                f"del original ({len(bigrams)} estados, {len(all_chars)} chars únicos). "
                f"Distribución de bigrams similar al original — LZ y entropía de "
                f"primer orden se mantienen cerca. Semánticamente incoherente. "
                f"Modela adversario que calibra frecuencias para evadir filtros estadísticos."
            ),
        )


# ---------------------------------------------------------------------------
# GAP-09 — TieBreakMutator
# ---------------------------------------------------------------------------

class TieBreakMutator:
    """
    GAP-09: tie_break_exploitation

    Genera secuencias con muchos valores iguales adyacentes. En el
    cálculo de Permutation Entropy (PE), empates en los valores fuerzan
    el algoritmo de stable-sort a un comportamiento específico. Un
    adversario que conoce el algoritmo puede construir inputs que
    producen PE artificialmente bajo o alto.

    El P2_SPEC §14 documenta este gap como "determinístico pero
    adversarialmente explotable". Este vector verifica que el motor
    PE no produce resultados semánticamente incorrectos bajo empates
    extremos.
    """

    def mutate(
        self,
        text: str,
        tie_fraction: Fraction = Fraction(6, 10),
        fill_value: int = 32,  # ASCII espacio — neutro semánticamente
        seed: int = 42,
    ) -> MutationResult:
        """
        Reemplaza exactamente `tie_fraction` de los caracteres por `fill_value`,
        forzando empates masivos en la distribución de valores ordinales.

        CORRECCIÓN Fix 5 (Anna Tchijova, 2026-05-18):
        La versión anterior usaba:
            positions = sorted(set(r % n for r in rng))[:n_ties]
        lo que producía cardinalidad efectiva < n_ties debido a colisiones
        del módulo + deduplicación, sin ningún warning. La intensidad reportada
        divergía silenciosamente de la pedida.

        Esta versión usa rejection sampling determinista: genera valores LCG
        hasta tener exactamente n_ties posiciones únicas, o hasta agotar
        MAX_ATTEMPTS = n_ties * 8. Si no alcanza la cardinalidad exacta,
        reporta la intensidad_efectiva real y emite warning en description.

        Args:
            text          : artefacto original
            tie_fraction  : fracción de caracteres a homogeneizar
            fill_value    : valor ordinal de relleno (default: espacio ASCII)
            seed          : semilla determinista
        """
        if not text:
            raise ValueError("TieBreakMutator: text no puede estar vacío")
        if not (Fraction(0) < tie_fraction <= Fraction(1)):
            raise ValueError("TieBreakMutator: tie_fraction debe estar en (0, 1]")

        n = len(text)
        n_ties = int(n * float(tie_fraction))

        # Rejection sampling determinista
        MAX_ATTEMPTS = max(n_ties * 8, 64)
        rng = _lcg(seed, MAX_ATTEMPTS)
        positions: List[int] = []
        seen: set = set()
        for r in rng:
            if len(positions) >= n_ties:
                break
            p = r % n
            if p not in seen:
                seen.add(p)
                positions.append(p)

        positions.sort()
        effective = len(positions)
        intensity_requested = Fraction(n_ties, max(n, 1))
        intensity_effective = Fraction(effective, max(n, 1))
        shortfall = n_ties - effective
        intensity_warning = shortfall > 0

        chars = list(text)
        for pos in positions:
            chars[pos] = chr(fill_value)

        mutated = "".join(chars)

        description = (
            f"Homogeneización de {effective}/{n} caracteres "
            f"con valor ordinal {fill_value} ('{chr(fill_value)}'). "
            f"La distribución de PE tiene {effective} empates forzados. "
            f"Verifica robustez del stable-sort ante distribuciones degeneradas."
        )
        if intensity_warning:
            description += (
                f" ADVERTENCIA: intensidad pedida={float(intensity_requested):.3f} "
                f"({n_ties} posiciones), efectiva={float(intensity_effective):.3f} "
                f"({effective} posiciones). Shortfall={shortfall} — "
                f"LCG agotó {MAX_ATTEMPTS} intentos antes de cubrir cardinalidad exacta."
            )

        return MutationResult(
            mutator_name="TieBreakMutator",
            gap_ids=["GAP-09"],
            original_text=text,
            mutated_text=mutated,
            mutation_params={
                "tie_fraction":          str(tie_fraction),
                "fill_value":            fill_value,
                "fill_char":             chr(fill_value),
                "seed":                  seed,
                "n_ties_requested":      n_ties,
                "n_ties_effective":      effective,
                "intensity_requested":   str(intensity_requested),
                "intensity_effective":   str(intensity_effective),
                "max_attempts":          MAX_ATTEMPTS,
                "intensity_shortfall":   shortfall,
            },
            intensity=intensity_effective,
            description=description,
        )


# ---------------------------------------------------------------------------
# GAP-10 — PeriodAliasingMutator
# ---------------------------------------------------------------------------

class PeriodAliasingMutator:
    """
    GAP-10: lz_period_aliasing

    LZ76 usa normalización asintótica c(n) / (n / log2(n)).
    Para secuencias cortas con períodos cercanos a sqrt(n), el
    score normalizado puede malrepresentar la compresibilidad real.

    Este mutador genera secuencias con períodos exactamente en
    la zona de aliasing (cerca de sqrt(n)) para verificar que
    el engine LZ detecta el problema en lugar de producir un
    score silenciosamente incorrecto.
    """

    def mutate(
        self,
        text: str,
        seed: int = 42,
    ) -> MutationResult:
        """
        Genera una versión del texto con período exactamente en sqrt(len(text)).
        Si el texto es demasiado corto (<= 9 caracteres), lanza ValueError.
        """
        if not text:
            raise ValueError("PeriodAliasingMutator: text no puede estar vacío")

        n = len(text)
        if n < 9:
            raise ValueError(
                f"PeriodAliasingMutator: text demasiado corto (n={n}). "
                f"GAP-10 requiere n >= 9 para que sqrt(n) >= 3."
            )

        # Período objetivo: floor(sqrt(n))
        period = max(1, int(n ** 0.5))
        rng = _lcg(seed, 1)
        start = rng[0] % max(1, n - period)
        token = text[start : start + period]
        if not token:
            token = text[:period]

        repetitions = (n // len(token)) + 1
        mutated = (token * repetitions)[:n]

        # Verificación interna: el período es efectivamente cercano a sqrt(n)
        aliasing_zone = abs(period - (n ** 0.5)) / max(n ** 0.5, 1)

        return MutationResult(
            mutator_name="PeriodAliasingMutator",
            gap_ids=["GAP-10"],
            original_text=text,
            mutated_text=mutated,
            mutation_params={
                "n":              n,
                "period":         period,
                "sqrt_n":         _dround(n ** 0.5, _DETERMINISTIC_OUTPUT_PREC),
                "aliasing_zone":  _dround(aliasing_zone, _DETERMINISTIC_OUTPUT_PREC),
                "token":          token,
                "seed":           seed,
            },
            intensity=Fraction(1, 1),
            description=(
                f"Secuencia con período {period} ≈ sqrt({n})={n**0.5:.2f}. "
                f"En la zona de aliasing LZ76 ({aliasing_zone:.3f} del sqrt(n)). "
                f"El score LZ normalizado puede ser semánticamente incorrecto "
                f"para esta longitud. El engine DEBE documentar la incertidumbre."
            ),
        )


# ---------------------------------------------------------------------------
# Orquestador — genera suite completa
# ---------------------------------------------------------------------------

class AdversarialMutationSuite:
    """
    Orquestador de la suite completa de mutaciones adversariales.

    Uso típico (desde adversarial_robustness.py o desde CLI de auditoría):

        suite = AdversarialMutationSuite()
        results = suite.run_all(artifact_text, seed=42)
        report = suite.to_report(results)

    El report es un dict JSON-serializable apto para incluir en
    el bundle forense como evidencia de auditoría de robustez.
    """

    def __init__(self) -> None:
        self._mutators = {
            "NoiseInjectionMutator":  NoiseInjectionMutator(),
            "SymbolExplosionMutator": SymbolExplosionMutator(),
            "FalseStructureMutator":  FalseStructureMutator(),
            "TieBreakMutator":        TieBreakMutator(),
            "PeriodAliasingMutator":  PeriodAliasingMutator(),
        }

    def run_all(
        self,
        text: str,
        seed: int = 42,
        skip_gaps: Optional[List[str]] = None,
    ) -> List[MutationResult]:
        """
        Ejecuta todos los mutadores sobre el texto dado.

        Args:
            text      : artefacto a perturbar
            seed      : semilla global (cada mutador deriva su seed de esta)
            skip_gaps : lista de GAP IDs a omitir (para auditorías parciales)

        Returns:
            Lista de MutationResult, uno por mutador ejecutado.
            Los mutadores que fallan con ValueError son capturados y
            reportados como errores — nunca se propagan silenciosamente.
        """
        if not text:
            raise ValueError("AdversarialMutationSuite.run_all: text no puede estar vacío")

        skip = set(skip_gaps or [])
        results: List[MutationResult] = []

        mutator_seeds = {
            name: (seed + i * 1000) & 0xFFFFFFFF
            for i, name in enumerate(sorted(self._mutators.keys()))
        }

        for name, mutator in self._mutators.items():
            gaps = GAP_MAP.get(name, [])
            if skip and all(g in skip for g in gaps):
                continue

            mseed = mutator_seeds[name]
            try:
                if isinstance(mutator, NoiseInjectionMutator):
                    result = mutator.mutate(text, seed=mseed)
                elif isinstance(mutator, SymbolExplosionMutator):
                    result = mutator.mutate(text, seed=mseed)
                elif isinstance(mutator, FalseStructureMutator):
                    result = mutator.mutate(text, seed=mseed)
                elif isinstance(mutator, TieBreakMutator):
                    result = mutator.mutate(text, seed=mseed)
                elif isinstance(mutator, PeriodAliasingMutator):
                    result = mutator.mutate(text, seed=mseed)
                else:
                    continue
                results.append(result)

            except ValueError as exc:
                # Crear resultado de error — no ocultar el fallo
                results.append(MutationResult(
                    mutator_name=name,
                    gap_ids=gaps,
                    original_text=text,
                    mutated_text=text,
                    mutation_params={"error": str(exc), "seed": mseed},
                    intensity=Fraction(0),
                    description=f"MUTACIÓN FALLIDA: {exc}",
                ))

        return results

    def to_report(
        self,
        results: List[MutationResult],
        artifact_id: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Serializa los resultados a un dict JSON-serializable.
        Apto para embeber en ForensicBundle como sección de auditoría.
        """
        covered_gaps = sorted({g for r in results for g in r.gap_ids})
        all_gaps = sorted({g for gaps in GAP_MAP.values() for g in gaps})
        uncovered_gaps = [g for g in all_gaps if g not in covered_gaps]

        return {
            "module":            MODULE_NAME,
            "version":           VERSION,
            "artifact_id":       artifact_id,
            "n_mutators":        len(results),
            "covered_gaps":      covered_gaps,
            "uncovered_gaps":    uncovered_gaps,
            "coverage_fraction": (
                str(Fraction(len(covered_gaps), max(len(all_gaps), 1)))
            ),
            "credit": {
                "inspiration": "Soedov, M. (2024). Agentic Security. "
                               "https://github.com/msoedov/agentic_security",
                "note": (
                    "Mutation families conceptually inspired by Soedov's "
                    "adversarial dataset mutation engine. "
                    "Implementation is original VIGÍA code operating on "
                    "forensic artifacts (not LLM prompts), with explicit "
                    "mapping to P2_SPEC §14 adversarial gaps."
                ),
            },
            "results": [r.to_dict() for r in results],
        }

    def check_noise_neutralized(
        self,
        original: str,
        result: MutationResult,
    ) -> bool:
        """
        Verifica que normalize_for_entropy() neutraliza la mutación de ruido.
        True si normalize_for_entropy(mutado) == normalize_for_entropy(original).

        Relevante para GAP-01 (NoiseInjectionMutator): los zero-width spaces
        deben desaparecer tras control_strip. NFKC solo NO es suficiente.

        Args:
            original : texto original pre-mutación
            result   : MutationResult de NoiseInjectionMutator

        Returns:
            True si la normalización correcta elimina el ruido inyectado.
        """
        return normalize_for_entropy(result.mutated_text) == normalize_for_entropy(original)

    def check_homoglyph_neutralized(
        self,
        original: str,
        result: MutationResult,
    ) -> bool:
        """
        Verifica que normalize_for_visual_equivalence() neutraliza homoglifos.
        True si normalize_for_visual_equivalence(mutado) == normalize_for_visual_equivalence(original).

        Relevante para GAP-02 (SymbolExplosionMutator): cirílicos y griegos
        deben colapsar al equivalente latino via confusable_map.
        NFKC + casefold solos NO son suficientes.

        Args:
            original : texto original pre-mutación
            result   : MutationResult de SymbolExplosionMutator

        Returns:
            True si la normalización de equivalencia visual colapsa los homoglifos.
            False si el mutator produjo diferencias no cubiertas por el mapa actual
            (señal de que el confusable_map necesita extensión).
        """
        return (
            normalize_for_visual_equivalence(result.mutated_text)
            == normalize_for_visual_equivalence(original)
        )


# ---------------------------------------------------------------------------
# CLI mínima para uso desde vigia_ask.sh
# ---------------------------------------------------------------------------

def _cli_demo() -> None:  # pragma: no cover
    sample = (
        "2026-05-18T03:14:22Z AUDIT_SUCCESS user=admin src=10.0.0.1 "
        "action=EXPORT_CREDENTIALS target=shadow_db bytes=4096 "
        "pid=1337 ppid=1 session=tty0 result=OK"
    )
    suite = AdversarialMutationSuite()
    results = suite.run_all(sample, seed=42)
    report = suite.to_report(results, artifact_id="demo_log_entry")
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    _cli_demo()
