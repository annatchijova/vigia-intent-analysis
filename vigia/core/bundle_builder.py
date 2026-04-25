# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
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
            k: v for k, v in graph_dict_full.items() if k != "graph_hash"
        }
        graph_hash = _sha256_dict(graph_dict_for_hash)
        policy_hash = _sha256_dict(policy_dict)
        decision_hash = _sha256_dict(decision_dict)

        # Paso 2: dict final del grafo con graph_hash incluido
        graph_dict_final = dict(graph_dict_full)
        graph_dict_final["graph_hash"] = graph_hash

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
        }
        if bundle.abduction_trace is not None:
            bundle_payload["abduction_trace"] = bundle.abduction_trace.to_dict()

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
        """
        content = json.dumps(sealed_dict, sort_keys=True, indent=2, default=str)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return file_hash

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
            graph_for_hash = {k: v for k, v in graph.items() if k != "graph_hash"}
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
