"""
vigia/core/tool_log_chain.py
=============================
Writer y verificador del hash chain del tool_execution_log.

Historia — dos esquemas:

  v1 (legacy, bundles históricos en results/):
    prev_hash = SHA-256(result_summary del entry anterior), "GENESIS" en seq=1.
    DEBILIDAD DOCUMENTADA: solo result_summary está protegido. timestamp,
    tool, target, input_hash y event_id de cualquier entrada son editables
    sin romper la cadena, y el result_summary de la ÚLTIMA entrada es
    editable libremente (nada encadena después). Se mantiene solo para
    verificar bundles ya sellados — NO usar para escribir.

  v2 (actual — este módulo):
    entry_hash = SHA-256(canonical(entrada completa + seq + prev_hash))
    prev_hash  = entry_hash del entry anterior (GENESIS_HASH en seq=1)
    entry_hmac = HMAC-SHA256(VIGIA_HMAC_KEY, entry_hash)   [si hay clave]
    Cualquier campo alterado en cualquier entrada rompe la cadena.

El agente (Claude Code / MCP / pipeline) debe usar ToolExecutionLogChain
para generar entradas en vez de implementar el esquema a mano — el esquema
de CLAUDE.md es la especificación, este módulo es la implementación.

La verificación standalone stdlib-only para terceros vive en
verify_tool_log.py (raíz del repo), que mantiene su propia copia de la
canonicalización por diseño (mismo patrón que verify_ebs_v1.py).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from vigia.core.hash_chain import (
    CHAIN_SCHEMA_VERSION,
    GENESIS_HASH,
    ChainLink,
    ChainVerification,
    compute_entry_hash,
    compute_entry_hmac,
    resolve_hmac_key,
    verify_chain,
)

V1_GENESIS = "GENESIS"
RESULT_SUMMARY_MAX = 120  # esquema CLAUDE.md: truncado a 120 chars

# Campos estructurales de la cadena — todo lo demás entra al hash
_STRUCTURAL_FIELDS = frozenset({"seq", "prev_hash", "entry_hash", "entry_hmac"})


def _hashed_payload(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Payload de contenido de una entrada (sin los campos estructurales)."""
    return {k: v for k, v in entry.items() if k not in _STRUCTURAL_FIELDS}


class ToolExecutionLogChain:
    """
    Appender del tool_execution_log v2.

    Uso (agente / pipeline):
        chain = ToolExecutionLogChain(mode="claude_code")
        entry = chain.append(
            tool="generate_forensic_hash",
            target="/evidence/disk.img",
            result_summary="sha256=ab12... 4.2GB",
            arguments={"path": "/evidence/disk.img"},
        )
        bundle["tool_execution_log"].append(entry)

    La clave HMAC se resuelve una vez al construir (VIGIA_HMAC_KEY /
    VIGIA_HMAC_KEY_FILE). Sin clave → modo hash-only, documentado en
    cada entrada como hmac: ausente.
    """

    def __init__(self, mode: str = "claude_code",
                 hmac_key: Optional[bytes] = None,
                 use_env_key: bool = True) -> None:
        self.mode = mode
        self._seq = 0
        self._prev_hash = GENESIS_HASH
        self._hmac_key = hmac_key if hmac_key is not None else (
            resolve_hmac_key() if use_env_key else None
        )

    @property
    def tip_hash(self) -> str:
        """entry_hash del último eslabón — para checkpoints de punta."""
        return self._prev_hash

    @property
    def tip_hmac(self) -> Optional[str]:
        """HMAC-SHA256(clave, tip_hash) — None si no hay clave configurada."""
        if not self._hmac_key:
            return None
        return compute_entry_hmac(self._hmac_key, self._prev_hash)

    @property
    def length(self) -> int:
        return self._seq

    def bundle_fields(self) -> Dict[str, Any]:
        """
        Campos de nivel-bundle que anclan la cola de la cadena (R3-5):
        chain_tip_sha256 (siempre) y chain_tip_hmac (si hay clave HMAC).

        El caller los escribe como hermanos de tool_execution_log, FUERA del
        arreglo que un atacante truncaría:

            bundle["tool_execution_log"] = log
            bundle.update(chain.bundle_fields())

        Sin esto, borrar las últimas N entradas de tool_execution_log deja el
        resto de la cadena internamente válida — nada lo nota (ver docstring
        del módulo). chain_tip_sha256 detecta el ataque salvo que el atacante
        también lo recalcule; chain_tip_hmac cierra ese residual (requiere la
        clave, igual que entry_hmac para el resto de la cadena).
        """
        fields: Dict[str, Any] = {"chain_tip_sha256": self.tip_hash}
        tip_hmac = self.tip_hmac
        if tip_hmac is not None:
            fields["chain_tip_hmac"] = tip_hmac
        return fields

    def append(
        self,
        tool: str,
        target: str,
        result_summary: str,
        arguments: Optional[Dict[str, Any]] = None,
        *,
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera la siguiente entrada encadenada del log.

        event_id/timestamp son inyectables para runs deterministas de
        evaluación; en producción se generan acá (uuid4 / UTC ahora).
        input_hash = SHA-256 de los argumentos sanitizados como JSON
        canónico (sort_keys) — igual que el esquema v1.
        """
        self._seq += 1
        args_json = json.dumps(arguments or {}, sort_keys=True,
                               ensure_ascii=True, default=str)
        entry: Dict[str, Any] = {
            "seq": self._seq,
            "event_id": event_id or str(uuid.uuid4()),
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "tool": tool,
            "target": target,
            "result_summary": result_summary[:RESULT_SUMMARY_MAX],
            "input_hash": hashlib.sha256(args_json.encode("utf-8")).hexdigest(),
            "chain_version": CHAIN_SCHEMA_VERSION,
            "prev_hash": self._prev_hash,
        }
        entry_hash = compute_entry_hash(
            self._seq, self._prev_hash, _hashed_payload(entry)
        )
        entry["entry_hash"] = entry_hash
        if self._hmac_key:
            entry["entry_hmac"] = compute_entry_hmac(self._hmac_key, entry_hash)

        self._prev_hash = entry_hash
        return entry


# ──────────────────────────────────────────────────────────────────────────
# Verificación dual v1 / v2
# ──────────────────────────────────────────────────────────────────────────

def detect_chain_version(log: Sequence[Dict[str, Any]]) -> str:
    """v2 si la primera entrada trae entry_hash; v1 en caso contrario."""
    if log and log[0].get("entry_hash"):
        return "2"
    return "1"


def verify_tool_execution_log(
    log: Sequence[Dict[str, Any]],
    *,
    hmac_key: Optional[bytes] = None,
    expected_tip: Optional[str] = None,
    expected_tip_hmac: Optional[str] = None,
) -> ChainVerification:
    """
    Verifica un tool_execution_log completo, auto-detectando el esquema.

    v2 → verificación completa vía hash_chain.verify_chain (contenido
    completo + linkage + seq + HMAC si hay clave).
    v1 → verificación legacy: solo linkage de result_summary. El resultado
    marca hmac_checked=False y NO garantiza integridad de los demás campos
    (debilidad estructural de v1, ver docstring del módulo). expected_tip /
    expected_tip_hmac (R3-5) se ignoran bajo v1 — chain_tip_sha256 es un
    concepto v2, ver verify_bundle_tool_log.

    expected_tip/expected_tip_hmac (R3-5): pasar bundle["chain_tip_sha256"] /
    bundle["chain_tip_hmac"] aquí ancla la COLA del log — sin esto, borrar
    las últimas entradas deja el resto de la cadena internamente válida.
    """
    if detect_chain_version(log) == "2":
        links = [
            ChainLink(
                seq=e.get("seq", 0),
                prev_hash=e.get("prev_hash", ""),
                entry_hash=e.get("entry_hash", ""),
                payload=_hashed_payload(e),
                entry_hmac=e.get("entry_hmac"),
            )
            for e in log
        ]
        return verify_chain(
            links, first_seq=1, hmac_key=hmac_key,
            expected_tip=expected_tip, expected_tip_hmac=expected_tip_hmac,
        )

    # ── v1 legacy ──────────────────────────────────────────────────────
    result = ChainVerification(valid=True, length=len(log), hmac_checked=False)
    prev_summary: Optional[str] = None
    expected_seq = 1
    for e in log:
        seq = e.get("seq", 0)
        if seq != expected_seq:
            result.seq_discontinuities.append({
                "expected_seq": expected_seq, "found_seq": seq,
                "note": "discontinuidad de seq (esquema v1)",
            })
            result.valid = False
            if result.first_invalid_seq is None:
                result.first_invalid_seq = seq
            expected_seq = seq
        prev_hash = e.get("prev_hash", "")
        if seq == 1:
            ok = prev_hash == V1_GENESIS
        else:
            expected = (
                hashlib.sha256(prev_summary.encode("utf-8")).hexdigest()
                if prev_summary is not None else ""
            )
            ok = prev_hash == expected
        if not ok:
            result.broken_links.append({
                "seq": seq,
                "note": "prev_hash v1 no coincide con SHA-256(result_summary anterior)",
            })
            result.valid = False
            if result.first_invalid_seq is None or seq < result.first_invalid_seq:
                result.first_invalid_seq = seq
        prev_summary = e.get("result_summary", "")
        expected_seq = seq + 1
    return result


def verify_bundle_tool_log(
    bundle: Dict[str, Any],
    *,
    hmac_key: Optional[bytes] = None,
) -> Dict[str, Any]:
    """
    Conveniencia: verifica bundle["tool_execution_log"] y retorna un dict
    reportable (para incluir en amicus curiae / reportes).

    R3-5: si el bundle trae chain_tip_sha256 (y opcionalmente
    chain_tip_hmac), se usan para anclar la cola del log — ver
    ToolExecutionLogChain.bundle_fields y el docstring de verify_chain.
    Solo aplica bajo v2; chain_tip_sha256 es un concepto v2.
    """
    log: List[Dict[str, Any]] = bundle.get("tool_execution_log", [])
    version = detect_chain_version(log)
    expected_tip = bundle.get("chain_tip_sha256") if version == "2" else None
    expected_tip_hmac = bundle.get("chain_tip_hmac") if version == "2" else None
    verification = verify_tool_execution_log(
        log, hmac_key=hmac_key,
        expected_tip=expected_tip, expected_tip_hmac=expected_tip_hmac,
    )
    report = verification.to_dict()
    report["chain_version"] = version
    if version == "1":
        report["v1_caveat"] = (
            "Esquema v1: solo result_summary está protegido por la cadena. "
            "timestamp/tool/target/input_hash no son tamper-evident, y el "
            "result_summary de la última entrada es editable. Verificación "
            "estructural, no de contenido completo."
        )
    elif expected_tip is None:
        report["chain_tip_caveat"] = (
            "chain_tip_sha256 ausente del bundle: la cola de "
            "tool_execution_log puede truncarse (últimas entradas borradas) "
            "sin que la cadena interna lo detecte — la linkage solo prueba "
            "consistencia de lo que quedó, no completitud. Ver R3-5 en "
            "docs/REDTEAM_ROUND3_EMERGENT.md."
        )
    return report
