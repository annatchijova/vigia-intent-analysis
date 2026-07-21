"""
vigia/forensics/bundle_builder.py
─────────────────────────────────────────────────────────────────────────────
BundleBuilder — Proceso Externo de Atestacion Criptografica EBS v1

ARQUITECTURA: Capa 5 — Forensica

PROPOSITO:
    Sellar un ForensicBundle con hashes SHA-256 encadenados.
    Es un proceso externo al modelo de datos.

RAZON DEL DESACOPLAMIENTO (Gemini):
    Si seal() viviera dentro de ForensicBundle, un motor comprometido
    podria sellar su propia mentira. Al ser externo, el proceso de
    atestacion puede ser ejecutado por un agente independiente que
    no tiene acceso al runtime del motor de inferencia.

PROTOCOLO DE HASHING:
    1. graph_hash   = SHA256(graph_dict sin el campo graph_hash)
       [El campo graph_hash es el resultado — no puede ser input de si mismo]
    2. policy_hash  = SHA256(policy_dict)
    3. decision_hash = SHA256(decision_dict)
    4. evidence_graph con graph_hash asignado -> graph_dict_final
    5. bundle_hash  = SHA256(bundle_id + version + timestamp +
                             graph_dict_final + decision_dict +
                             policy_dict + actions + system_state)
       [bundle_hash cubre TODO — Invariante I2]

SALIDA:
    dict sellado compatible con verify_ebs_v1.py y con SIFT.
    El verificador puede validarlo sin importar este modulo.

INDEPENDENCIA DEL VERIFICADOR:
    verify_ebs_v1.py implementa la misma logica de hashing con stdlib puro.
    No importa bundle_builder.py. Es deliberado — son dos mundos separados.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Resolucion de raiz — patron blindado (DeepSeek)
# El sistema debe saber donde esta parado sin importar desde donde se ejecuta.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # <repo>/vigia — used ONLY for the attestation

logger = logging.getLogger(__name__)
# source scan below. B-097 root cause: this used to be sys.path.insert(0,
# _ROOT), which shadowed every top-level package sharing a name with a
# vigia/ subpackage (forensics, pki_tools, ...) for the whole process. All
# imports in this module are vigia.-qualified; the insert served nothing.

from vigia.core.ebs_v1 import (
    ForensicBundle, IntegrityBlock, EBS_VERSION,
)
from vigia.security.output_boundary import validate_external_output_path


# ---------------------------------------------------------------------------
# Hash helpers — identicos a los de verify_ebs_v1.py (no importar desde alli)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Canonicalización — copia local (lockstep con vigia/core/canonicalize.py,
# verificado por tests/test_canonicalize_lockstep.py). v2 es el default de
# sellado; v1 se conserva para verificar bundles historicos (R3-2).
# ---------------------------------------------------------------------------
import unicodedata as _unicodedata
from fractions import Fraction as _Fraction

_V2_STR_PREFIX = "s:"


def _v2_norm_str(s: str) -> str:
    return _unicodedata.normalize("NFC", s.replace("\r\n", "\n").replace("\r", "\n"))


def _canonicalize_v1(obj: Any) -> Any:
    """Esquema v1 (LEGACY — solo verificacion de bundles historicos)."""
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:          # NaN
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
    Esquema v2 (R3-2) — DEFAULT. Escalares identicos a v1; strings escapados
    (s: + NFC/CRLF->LF); Fraction explicito. Cierra las colisiones de tipo
    (True/"true", 1/"1:int", None/"null", NFC/NFD, CRLF/LF).
    """
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        if obj != obj:          # NaN
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
    """Forma canonica DEFAULT (v2). Ver _canonicalize_v2 / canonicalize.py."""
    return _canonicalize_v2(obj)


def _sha256_dict(obj: Dict, canon=_canonicalize) -> str:
    """
    SHA-256 determinístico de un dict con forma canónica estricta (H22).

    `canon` elige el esquema (default v2). La verificacion prueba v2 y cae a v1
    para bundles historicos (R3-2).
    """
    canonical = canon(obj)
    serialized = json.dumps(canonical, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _sha256_dict_matches(obj: Dict, stored: str) -> bool:
    """True si el hash de `obj` recomputa bajo v2 O v1 (R3-2 backward-compat)."""
    return any(
        _sha256_dict(obj, canon=c) == stored
        for c in (_canonicalize_v2, _canonicalize_v1)
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# BundleBuilder — atestador externo
# ---------------------------------------------------------------------------

class BundleBuilder:
    """
    Proceso externo de atestacion criptografica para ForensicBundle.

    Uso:
        bundle = ForensicBundle(graph, trace, policy, actions, state)
        sealed = BundleBuilder.seal(bundle)
        path = BundleBuilder.save(sealed, "output/bundle.json")
        # => python3 forensics/verify_ebs_v1.py output/bundle.json
    """

    @staticmethod
    def seal(
        bundle: ForensicBundle,
        engine_attestation_hash: str = "",
        ecl_hash: str = "",
        caie_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sella el bundle produciendo un dict JSON completo con hashes encadenados.

        PROTOCOLO (identico al que implementa verify_ebs_v1.py):

        Paso 1: graph_hash sobre el grafo SIN el campo graph_hash
                (evita autorreferencia circular)
        Paso 2: Asignar graph_hash al grafo y tomar snapshot final
        Paso 3: bundle_hash sobre snapshot_final (incluye graph_hash)

        Retorna un dict serializable listo para SIFT.
        No modifica el objeto ForensicBundle original.
        """
        # Snapshot inmutable del contenido en este momento
        graph_dict_full = bundle.evidence_graph.to_dict()
        policy_dict = bundle.policy_spec.to_dict()
        decision_dict = bundle.decision_trace.to_dict()
        actions_list = [a.to_dict() for a in bundle.actions]
        state_dict = bundle.system_state.to_dict()

        # Paso 1: graph_hash excluye el campo graph_hash del grafo
        graph_dict_for_hash = {
            k: v for k, v in graph_dict_full.items() if k not in ("graph_hash", "generated_at")
        }
        graph_hash = _sha256_dict(graph_dict_for_hash)
        policy_dict_for_hash = {k: v for k, v in policy_dict.items() if k != "created_at"}
        policy_hash = _sha256_dict(policy_dict_for_hash)
        decision_hash = _sha256_dict(decision_dict)

        # Paso 2: dict final del grafo con graph_hash incluido
        graph_dict_final = dict(graph_dict_full)
        graph_dict_final["graph_hash"] = graph_hash

        # Config attestation — auto-documentación de configuración para Daubert
        config_attestation = {
            "vigia_version": bundle.bundle_version,
            "config_hash": "",
            "deviation_from_canonical": False,
            "modified_params": [],
            "canonical_version": "1.0.0",
        }
        if caie_analysis is not None:
            config_attestation["caie_enabled"] = True
            config_attestation["caie_verdict"] = caie_analysis.get("verdict", "UNKNOWN")

        # Paso 3: bundle_hash cubre TODO (I2)
        # abduction_trace se incluye si existe — es parte de la prueba auditorial
        bundle_payload = {
            "bundle_id": bundle.bundle_id,
            "bundle_version": bundle.bundle_version,
            "timestamp": bundle.timestamp,
            "evidence_graph": graph_dict_final,
            "decision_trace": decision_dict,
            "policy_spec": policy_dict,
            "actions": actions_list,
            "system_state": state_dict,
            "config_attestation": config_attestation,
        }
        if bundle.abduction_trace is not None:
            bundle_payload["abduction_trace"] = bundle.abduction_trace.to_dict()
        if caie_analysis is not None:
            bundle_payload["caie_analysis"] = caie_analysis
        
        # Calcular config_hash
        config_for_hash = dict(config_attestation)
        config_for_hash["caie_enabled"] = caie_analysis is not None
        bundle_payload["config_attestation"]["config_hash"] = _sha256_dict(config_for_hash)

        bundle_hash = _sha256_dict(bundle_payload)

        integrity = IntegrityBlock(
            bundle_hash=bundle_hash,
            graph_hash=graph_hash,
            policy_hash=policy_hash,
            decision_hash=decision_hash,
            engine_attestation_hash=engine_attestation_hash,
            ecl_hash=ecl_hash,
        )

        # Asignar al objeto original para referencia en memoria
        bundle.integrity = integrity

        # Producir el dict sellado completo
        sealed = dict(bundle_payload)
        sealed["integrity"] = integrity.to_dict()

        return sealed

    @staticmethod
    def save(sealed_dict: Dict[str, Any], path: str) -> str:
        """
        Guarda el bundle sellado en disco.
        Retorna el hash del archivo para verificacion de transporte.

        L-023 FIX (SEC-04): escritura ATÓMICA — mkstemp en el mismo
        directorio + fsync + os.replace. Antes se escribía directo sobre
        `path` sin fsync ni rename atómico: entre el write y el cómputo del
        hash (que además se calculaba desde memoria, no desde disco) el
        archivo podía ser swapeado (symlink attack / escritor concurrente) —
        ruptura de cadena de custodia bajo Daubert. Ahora:
          1. el contenido se escribe en un tempfile del mismo filesystem,
          2. fsync garantiza que llegó a disco,
          3. os.replace lo publica atómicamente (nunca hay un bundle a
             medio escribir visible en `path`),
          4. el hash retornado se computa DESDE DISCO post-replace y se
             verifica contra el hash en memoria — divergencia = RuntimeError.
        """
        import tempfile

        # B-183: a sealed bundle is derived output, never source evidence.
        # Validate before creating a parent directory and again immediately
        # before publication, because ``path`` carries write authority.
        abs_path = validate_external_output_path(
            path, artifact_label="sealed forensic bundle"
        )
        content = json.dumps(sealed_dict, sort_keys=True, indent=2, default=str)
        target_dir = os.path.dirname(abs_path)
        os.makedirs(target_dir, exist_ok=True)
        abs_path = validate_external_output_path(
            abs_path, artifact_label="sealed forensic bundle"
        )
        target_dir = os.path.dirname(abs_path)

        mem_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        fd, tmp_path = tempfile.mkstemp(
            dir=target_dir, prefix=".bundle_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, abs_path)
        except BaseException:
            # No dejar tempfiles huérfanos si algo falla antes del replace.
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        # Hash desde disco: lo que se verifica es lo que quedó escrito,
        # no lo que estaba en memoria.
        with open(abs_path, "rb") as f:
            disk_hash = hashlib.sha256(f.read()).hexdigest()
        if disk_hash != mem_hash:
            raise RuntimeError(
                f"L-023: hash en disco difiere del hash en memoria tras la "
                f"escritura atómica ({disk_hash[:16]} != {mem_hash[:16]}) — "
                f"posible corrupción de filesystem o tampering concurrente."
            )
        return disk_hash

    @staticmethod
    def quick_verify(sealed_dict: Dict[str, Any]) -> tuple:
        """
        Verificacion interna rapida (no reemplaza verify_ebs_v1.py).
        Reimplementa la logica de hashing sin llamar al verificador externo.

        Retorna: (is_valid: bool, message: str)
        """
        try:
            integrity = sealed_dict.get("integrity", {})
            stored_bundle_hash = integrity.get("bundle_hash", "")
            stored_graph_hash = integrity.get("graph_hash", "")

            # Verificar graph_hash (prueba v2 y cae a v1 — R3-2)
            graph = sealed_dict.get("evidence_graph", {})
            graph_for_hash = {k: v for k, v in graph.items() if k not in ("graph_hash", "generated_at")}
            if not _sha256_dict_matches(graph_for_hash, stored_graph_hash):
                recomputed_graph = _sha256_dict(graph_for_hash)
                return False, f"graph_hash invalido: {recomputed_graph[:8]}!={stored_graph_hash[:8]}"

            # Verificar bundle_hash (prueba v2 y cae a v1 — R3-2)
            payload = {
                k: v for k, v in sealed_dict.items() if k != "integrity"
            }
            if not _sha256_dict_matches(payload, stored_bundle_hash):
                recomputed_bundle = _sha256_dict(payload)
                return False, f"bundle_hash invalido: {recomputed_bundle[:8]}!={stored_bundle_hash[:8]}"

            return True, "OK — bundle integro"

        except Exception as e:
            return False, f"Error en quick_verify: {e}"

    @staticmethod
    def compute_engine_attestation(
        source_dirs: Optional[list] = None,
        dep_files: Optional[list] = None,
    ) -> str:
        """
        Calcula engine_attestation_hash sobre código fuente + versiones de dependencias.

        hash(código_fuente + requirements.txt + pyproject.toml)

        H32: El motor es el código + sus librerías. Si alguien cambia la versión
        de sklearn o numpy, el KDE produce resultados distintos con el mismo código.
        El attestation debe capturar ambas dimensiones para ser válido ante Daubert.

        Solo incluye archivos .py de código fuente. Excluye:
        - __pycache__/ y cualquier .pyc / .pyo (H7)
        - Archivos temporales del SO (*.tmp, *.swp, *~, .DS_Store)
        - Logs y archivos de cobertura (*.log, .coverage)

        V-1 (docs/PATTERN_HUNT_20260718.md, 2026-07-18): la caminata cubre el
        árbol vigia/ (_ROOT), pero los módulos de decisión que viven en la RAÍZ
        del repo — vigia_scorer.py, vigia_agent.py, sift_orchestrator.py, los
        mismos tres que pyproject.toml declara como "the sealed verdict
        pipeline" (--cov) — quedaban fuera: cambiarlos dejaba
        engine_attestation_hash byte-idéntico. La frontera residual documentada
        nombraba solo vigia_scorer.py, ocultando los otros dos. Ahora, EN MODO
        DEFAULT (source_dirs is None), los tres se pliegan al hash con la misma
        degradación honesta (ausente/ilegible → marcador que perturba, nunca
        desaparición silenciosa). Con source_dirs explícito el comportamiento
        no cambia (los tests que pasan un dir temporal siguen viendo solo ese
        dir). caie_legacy_root.py queda fuera a propósito: ningún módulo de
        runtime lo importa (código muerto), no está en el decision path.
        """
        _EXCLUDED_DIRS = {"__pycache__", ".git", ".mypy_cache", ".ruff_cache", "node_modules"}
        _EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".swp", ".log", ".coverage"}
        _EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}

        # Módulos de decisión en la raíz del repo (fuera de _ROOT=<repo>/vigia).
        # Set autoritativo = el --cov de pyproject.toml. Ordenado para
        # determinismo. Solo se pliegan en modo default (V-1).
        _ROOT_DECISION_MODULES = (
            "sift_orchestrator.py",
            "vigia_agent.py",
            "vigia_scorer.py",
        )

        # Archivos de dependencias a incluir (H32)
        _DEFAULT_DEP_FILES = ["requirements.txt", "pyproject.toml"]

        try:
            dirs = source_dirs or [_ROOT]
            sources = []

            # 1. Código fuente .py
            for d in dirs:
                for root, subdirs, files in os.walk(d):
                    subdirs[:] = sorted(
                        s for s in subdirs if s not in _EXCLUDED_DIRS
                    )
                    for fname in sorted(files):
                        if not fname.endswith(".py"):
                            continue
                        if fname in _EXCLUDED_NAMES:
                            continue
                        if any(fname.endswith(suf) for suf in _EXCLUDED_SUFFIXES):
                            continue
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, "rb") as f:
                                sources.append(f.read())
                        except OSError as exc:
                            # Honest degradation: an in-scope source file that
                            # cannot be read must PERTURB the attestation, never
                            # vanish silently. A silently dropped file lets two
                            # different engine states hash identically (coverage
                            # reduction presented as a complete attestation) and
                            # lets a file made unreadable escape the seal. Fold a
                            # deterministic unreadable-marker (path only, relative
                            # for reproducibility) into the hash and log it loud.
                            marker = f"UNREADABLE_SOURCE:{os.path.relpath(fpath, d)}\n"
                            sources.append(marker.encode("utf-8"))
                            logger.warning(
                                "engine attestation: source unreadable, folded "
                                "into hash as %s (%s)", marker.strip(), exc,
                            )

            # 1b. Módulos de decisión de la raíz del repo (V-1). Solo en modo
            # default: con source_dirs explícito el llamador define el scope.
            if source_dirs is None:
                _repo_root = os.path.dirname(_ROOT)
                for mod_name in _ROOT_DECISION_MODULES:  # ya ordenado
                    mpath = os.path.join(_repo_root, mod_name)
                    if not os.path.isfile(mpath):
                        # Un módulo de decisión declarado que falta DEBE perturbar
                        # el hash (no puede desaparecer en silencio): borrar
                        # vigia_scorer.py no puede dejar la attestation idéntica.
                        marker = f"MISSING_ROOT_MODULE:{mod_name}\n"
                        sources.append(marker.encode("utf-8"))
                        logger.warning(
                            "engine attestation: root decision module %s absent, "
                            "folded into hash as %s", mod_name, marker.strip(),
                        )
                        continue
                    try:
                        with open(mpath, "rb") as f:
                            sources.append(
                                f"ROOT:{mod_name}\n".encode("utf-8") + f.read()
                            )
                    except OSError as exc:
                        marker = f"UNREADABLE_ROOT_MODULE:{mod_name}\n"
                        sources.append(marker.encode("utf-8"))
                        logger.warning(
                            "engine attestation: root decision module %s present "
                            "but unreadable, folded into hash as %s (%s)",
                            mod_name, marker.strip(), exc,
                        )

            # 2. Archivos de dependencias (H32)
            dep_paths = dep_files if dep_files is not None else _DEFAULT_DEP_FILES
            for dep_name in dep_paths:
                # Buscar primero en _ROOT, luego en directorio padre
                candidates = [
                    os.path.join(_ROOT, dep_name),
                    os.path.join(os.path.dirname(_ROOT), dep_name),
                ]
                for candidate in candidates:
                    if os.path.isfile(candidate):
                        try:
                            with open(candidate, "rb") as f:
                                dep_content = f.read()
                            # Prefijo para distinguir deps de código fuente
                            sources.append(f"DEP:{dep_name}\n".encode("utf-8") + dep_content)
                        except OSError as exc:
                            # Same honest-degradation rule as source files: a dep
                            # manifest that is present but unreadable must perturb
                            # the hash, not silently drop out of the attestation.
                            sources.append(f"UNREADABLE_DEP:{dep_name}\n".encode("utf-8"))
                            logger.warning(
                                "engine attestation: dep %s present but unreadable, "
                                "folded into hash (%s)", dep_name, exc,
                            )
                        break  # Solo una vez por archivo

            combined = b"".join(sources)
            return hashlib.sha256(combined).hexdigest()
        except Exception:
            # A total attestation failure must not be silent: "" downstream reads
            # as "attestation unavailable" (R4 unreachable), which is the honest
            # outcome, but the failure itself must be logged, not swallowed.
            logger.exception("engine attestation computation failed — returning empty")
            return ""


# ---------------------------------------------------------------------------
# build_bundle — convenience wrapper para demo runner y test suite
#
# Construye un ForensicBundle desde el resultado de _vigia_score() y lo sella
# con BundleBuilder.seal(). Sin dependencia de VigiaPipeline.
#
# Mapeo forense → EBS DecisionVerdict:
#   MALICE    → REJECT
#   SUSPICION → ABSTAIN
#   NOISE     → ACCEPT
#   UNKNOWN   → ABSTAIN
#
# El veredicto forense original se preserva en caie_analysis.verdict.
# ---------------------------------------------------------------------------

def build_bundle(case: Dict[str, Any], scorer_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sella un ForensicBundle desde el resultado directo de _vigia_score().

    Permite a run_vigia_case.py mostrar los 4 hashes forenses sin pasar
    por VigiaPipeline completo. Equivalente forense al sellado del agente.

    Args:
        case          : dict del caso VIGÍA (schema legacy o EBS v1)
        scorer_result : dict retornado por _vigia_score(case)

    Returns:
        sealed_dict : bundle sellado listo para verify_ebs_v1.py y SIFT
    """
    from vigia.core.ebs_v1 import (
        EvidenceEdge, EvidenceGraph,
        DecisionTrace, SystemState,
        ForensicBundle, AbductionTrace,
        make_default_policy,
    )

    # ── EvidenceGraph desde effective_trusts ─────────────────────────────────
    effective_trusts = scorer_result.get("effective_trusts") or []
    nodes = [et["artifact_id"] for et in effective_trusts]
    if not nodes:
        nodes = [
            a.get("id", a.get("artifact_id", f"artifact_{i}"))
            for i, a in enumerate(case.get("artifacts", []))
        ]
    if not nodes:
        nodes = ["no_artifacts"]

    mean_trust = float(scorer_result.get("mean_effective_trust") or 0.5)
    edges = []
    for i in range(len(nodes) - 1):
        et_i = effective_trusts[i] if i < len(effective_trusts) else {}
        trust_i = float(et_i.get("effective_trust", mean_trust))
        edges.append(EvidenceEdge(
            source=nodes[i],
            target=nodes[i + 1],
            stability=trust_i,
            weight_mean=trust_i,
        ))

    graph = EvidenceGraph(nodes=nodes, edges=edges)

    # ── DecisionTrace: mapeo veredicto forense → EBS DecisionVerdict ─────────
    _VERDICT_MAP = {
        "MALICE":    "REJECT",
        "SUSPICION": "ABSTAIN",
        "NOISE":     "ACCEPT",
        "UNKNOWN":   "ABSTAIN",
    }
    raw_verdict = scorer_result.get("verdict", "UNKNOWN")
    decision_verdict = _VERDICT_MAP.get(raw_verdict, "ABSTAIN")
    score      = float(scorer_result.get("score", 0.0) or 0.0)
    confidence = float(scorer_result.get("confidence", 0.0) or 0.0)
    confidence = min(1.0, max(0.0, confidence))

    decision_trace = DecisionTrace(
        decision=decision_verdict,
        posterior=confidence,
        risk=score,
        reason_code=f"VIGIA_SCORER:{raw_verdict}",
    )

    # ── PolicySpec y SystemState ──────────────────────────────────────────────
    policy = make_default_policy()
    state  = SystemState(
        drift_score=0.0,
        graph_stability_global=mean_trust,
    )

    # ── AbductionTrace desde peirce_chain (opcional) ──────────────────────────
    peirce = scorer_result.get("peirce_chain") or {}
    abduction_trace = None
    if peirce:
        abduction_trace = AbductionTrace(
            peirce_firstness=peirce.get("firstness", ""),
            peirce_secondness=peirce.get("secondness", ""),
            peirce_thirdness=peirce.get("thirdness", ""),
            inference_mode="STANDALONE_SCORER",
        )

    # ── Construir bundle ──────────────────────────────────────────────────────
    bundle = ForensicBundle(
        evidence_graph=graph,
        decision_trace=decision_trace,
        policy_spec=policy,
        system_state=state,
        abduction_trace=abduction_trace,
    )

    # ── caie_analysis: veredicto forense completo para el bundle ──────────────
    caie_payload: Dict[str, Any] = {
        "verdict":               raw_verdict,
        "composite_score":       score,
        "confidence":            confidence,
        "caie_fractures":        int(scorer_result.get("caie_fractures", 0) or 0),
        "caie_fractures_source": scorer_result.get("caie_fractures_source", "standalone"),
        "hard_temporal_gate":    bool(scorer_result.get("hard_temporal_gate", False)),
        "peirce_chain":          peirce,
        "quadripartite_state":   scorer_result.get("quadripartite_state") or {},
        "reason":                scorer_result.get("reason", ""),
        "case_id":               case.get("case_id", case.get("name", "UNKNOWN")),
    }

    # R7 — deterministic devil_advocate. Never overwrites a human-provided
    # value because this path (_vigia_score / build_bundle) never had one.
    # pattern_signal_metadata is always None here: CasePatternLibrary only
    # runs inside sift_orchestrator.py, a separate code path — confirmed by
    # direct audit of vigia_scorer.py, not assumed. The composer falls back
    # to an explicit scope-limitation narrative instead of a generic template.
    if raw_verdict in ("MALICE", "INTENT"):
        from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
        caie_payload["devil_advocate"] = compose_devil_advocate_struct(
            pattern_signal_metadata=None,
            raw_verdict=raw_verdict,
            mapped_verdict=decision_verdict,
            score=score,
            confidence=confidence,
            scope_note="standalone scorer mode (vigia/core/bundle_builder.py build_bundle())",
        )

    return BundleBuilder.seal(bundle, caie_analysis=caie_payload)
