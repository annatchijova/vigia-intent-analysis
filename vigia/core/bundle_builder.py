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
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Resolucion de raiz — patron blindado (DeepSeek)
# El sistema debe saber donde esta parado sin importar desde donde se ejecuta.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from vigia.core.ebs_v1 import (
    ForensicBundle, IntegrityBlock, EBS_VERSION,
)


# ---------------------------------------------------------------------------
# Hash helpers — identicos a los de verify_ebs_v1.py (no importar desde alli)
# ---------------------------------------------------------------------------

def _canonicalize(obj: Any) -> Any:
    """
    Convierte recursivamente un objeto a forma canónica estricta para hasheo (H22).

    Problema: JSON no distingue int de float (1 vs 1.0 → strings distintos).
    Si el Optimizer produce un score como int y otro módulo lo lee como float,
    el bundle_hash cambia sin que el contenido haya cambiado — rompe Invariante I2.

    Reglas de canonicalización:
    - float  → string con 8 decimales fijos ("1.00000000")
    - int    → string con sufijo ":int" ("1:int") — diferencia de float(1)
    - bool   → "true" / "false" (minúsculas, antes de int porque bool es subclase)
    - None   → "null"
    - str    → sin cambios
    - dict   → keys ordenadas, valores recursivos
    - list   → elementos recursivos (orden preservado — listas son ordenadas)
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
        return f"{obj:.8f}"
    if isinstance(obj, str):
        return obj
    if obj is None:
        return "null"
    if isinstance(obj, dict):
        return {k: _canonicalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]
    # Fallback para tipos no reconocidos — str() para no romper el hash
    return str(obj)


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

        content = json.dumps(sealed_dict, sort_keys=True, indent=2, default=str)
        abs_path = os.path.abspath(path)
        target_dir = os.path.dirname(abs_path)
        os.makedirs(target_dir, exist_ok=True)

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

            # Verificar graph_hash
            graph = sealed_dict.get("evidence_graph", {})
            graph_for_hash = {k: v for k, v in graph.items() if k not in ("graph_hash", "generated_at")}
            recomputed_graph = _sha256_dict(graph_for_hash)
            if recomputed_graph != stored_graph_hash:
                return False, f"graph_hash invalido: {recomputed_graph[:8]}!={stored_graph_hash[:8]}"

            # Verificar bundle_hash
            payload = {
                k: v for k, v in sealed_dict.items() if k != "integrity"
            }
            recomputed_bundle = _sha256_dict(payload)
            if recomputed_bundle != stored_bundle_hash:
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
        """
        _EXCLUDED_DIRS = {"__pycache__", ".git", ".mypy_cache", ".ruff_cache", "node_modules"}
        _EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".swp", ".log", ".coverage"}
        _EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}

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
                        except OSError:
                            pass

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
                        except OSError:
                            pass
                        break  # Solo una vez por archivo

            combined = b"".join(sources)
            return hashlib.sha256(combined).hexdigest()
        except Exception:
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
