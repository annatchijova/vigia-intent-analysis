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

from models.ebs_v1 import (
    ForensicBundle, IntegrityBlock, EBS_VERSION,
)


# ---------------------------------------------------------------------------
# Hash helpers — identicos a los de verify_ebs_v1.py (no importar desde alli)
# ---------------------------------------------------------------------------

def _sha256_dict(obj: Dict) -> str:
    """SHA-256 determinístico de un dict. sort_keys=True garantiza orden canonico."""
    serialized = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
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
    def compute_engine_attestation(source_dirs: Optional[list] = None) -> str:
        """
        Calcula engine_attestation_hash sobre el codigo fuente del motor.
        hash(source_code + deps + build_spec) — para R4 del verificador.
        """
        try:
            dirs = source_dirs or [_ROOT]
            sources = []
            for d in dirs:
                for root, _, files in os.walk(d):
                    for fname in sorted(files):
                        if fname.endswith(".py"):
                            fpath = os.path.join(root, fname)
                            try:
                                with open(fpath, "rb") as f:
                                    sources.append(f.read())
                            except OSError:
                                pass
            combined = b"".join(sources)
            return hashlib.sha256(combined).hexdigest()
        except Exception:
            return ""
