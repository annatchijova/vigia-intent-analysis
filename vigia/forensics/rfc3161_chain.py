"""
vigia/forensics/rfc3161_chain.py
=================================
Cadena de custodia RFC 3161 para VIGÍA.

Provee timestamping de evidencia mediante TSA (Time Stamp Authority) externa.
La diferencia vs HMAC propio:
- HMAC dice "este archivo no cambió desde que VIGÍA lo procesó"
- RFC 3161 dice "un tercero independiente vio este hash en este momento"

Para Daubert: la diferencia entre el acusado certificando su propia inocencia
vs un testigo independiente haciéndolo.

TSAs gratuitas configuradas: FreeTSA (primaria), fallback local documentado.

Kimi fix: TSA local retorna JSON firmado que declara NOT_INDEPENDENT_WITNESS
en lugar de devolver el TSQ como si fuera TSR (engañoso).

Invariantes:
- CustodyRecord es frozen dataclass — inmutable
- tsa_token_b64 preserva token completo para verificación forense
- is_independent=False en reporte es visible al analista
"""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac_module
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Optional


# ─── TSA endpoints ───────────────────────────────────────────────────────────

TSA_ENDPOINTS: dict[str, dict] = {
    "freetsa": {
        "url":      "https://freetsa.org/tsr",
        "ca_note":  "Verify with freetsa.org/files/cacert.pem",
        "policy":   "1.2.840.113549.1.9.16.1.4",
        "independent": True,
    },
    "certum": {
        "url":      "http://time.certum.pl",
        "ca_note":  "Certum CA",
        "policy":   "public",
        "independent": True,
    },
    "local_hmac": {
        "url":      None,
        "ca_note":  "LOCAL HMAC — NOT AN INDEPENDENT WITNESS",
        "policy":   "internal",
        "independent": False,
    },
}


@dataclass(frozen=True)
class CustodyRecord:
    """
    Registro de custodia para un artefacto de evidencia.
    Inmutable por diseño — frozen dataclass.
    """
    artifact_path:    str
    artifact_sha256:  str
    artifact_sha512:  str
    artifact_size:    int
    ingest_timestamp: int       # Unix timestamp entero
    tsa_name:         str
    tsa_token_b64:    str       # Token RFC 3161 en base64 (opaco, para verificación forense)
    tsa_timestamp:    int       # Timestamp confirmado por la TSA
    tsa_policy:       str
    local_hmac:       str       # HMAC local como capa adicional
    is_independent:   bool      # False = no hay testigo independiente
    chain_position:   int


class RFC3161Timestamper:
    """
    Sellador de evidencia con timestamps RFC 3161.

    Flujo:
    1. Hash SHA-256 y SHA-512 del artefacto
    2. Construir TimeStampRequest (TSQ) manual
    3. Enviar a TSA externa
    4. Preservar token TSR completo
    5. Retornar CustodyRecord inmutable
    """

    def __init__(
        self,
        secret_key:   bytes,
        tsa_priority: list[str] | None = None,
        timeout_secs: int = 10,
    ):
        self._key     = secret_key
        self._prio    = tsa_priority or ["freetsa", "certum", "local_hmac"]
        self._timeout = timeout_secs
        self._chain:  list[CustodyRecord] = []

    # ── Hashing ───────────────────────────────────────────────────────────────

    def _hash_artifact(self, path: Path) -> tuple[str, str, int]:
        h256 = hashlib.sha256()
        h512 = hashlib.sha512()
        size = 0
        with open(path, "rb") as f:
            while chunk := f.read(65_536):
                h256.update(chunk)
                h512.update(chunk)
                size += len(chunk)
        return h256.hexdigest(), h512.hexdigest(), size

    # ── TSQ construction ──────────────────────────────────────────────────────

    def _build_tsq(self, sha256_hex: str) -> bytes:
        """
        Construye TimeStampRequest RFC 3161 mínimo sin dependencias externas.
        SHA-256 OID: 2.16.840.1.101.3.4.2.1
        """
        hash_bytes  = bytes.fromhex(sha256_hex)
        sha256_oid  = bytes([0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01])

        alg_oid_tlv    = b"\x06" + bytes([len(sha256_oid)]) + sha256_oid
        null_tlv       = b"\x05\x00"
        alg_identifier = b"\x30" + bytes([len(alg_oid_tlv + null_tlv)]) + alg_oid_tlv + null_tlv
        hashed_msg     = b"\x04" + bytes([len(hash_bytes)]) + hash_bytes
        msg_content    = alg_identifier + hashed_msg
        msg_imprint    = b"\x30" + bytes([len(msg_content)]) + msg_content

        version  = b"\x02\x01\x01"
        cert_req = b"\x01\x01\xff"
        tsq_content = version + msg_imprint + cert_req
        return b"\x30" + bytes([len(tsq_content)]) + tsq_content

    # ── TSA communication ─────────────────────────────────────────────────────

    def _send_tsq(self, tsq: bytes, tsa_name: str) -> Optional[bytes]:
        cfg = TSA_ENDPOINTS.get(tsa_name, {})
        url = cfg.get("url")
        if not url:
            return None

        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            url,
            data=tsq,
            headers={"Content-Type": "application/timestamp-query"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout, context=ctx) as resp:
                return resp.read() if resp.status == 200 else None
        except (urllib.error.URLError, OSError, TimeoutError):
            return None

    def _local_fallback_token(self, sha256_hex: str, timestamp: int) -> bytes:
        """
        Kimi fix: token local que declara explícitamente NOT_INDEPENDENT_WITNESS.
        No simula ser un TSR real — es un JSON firmado con HMAC local.
        """
        payload = {
            "warning":         "NOT_INDEPENDENT_WITNESS",
            "tsa_type":        "LOCAL_HMAC_FALLBACK",
            "sha256":          sha256_hex,
            "timestamp":       timestamp,
            "note":            (
                "Este token fue generado localmente. "
                "No hay testigo independiente. "
                "No usar como evidencia sin TSA externa."
            ),
        }
        canonical  = json.dumps(payload, sort_keys=True).encode()
        local_hmac = _hmac_module.new(self._key, canonical, hashlib.sha256).hexdigest()
        payload["local_hmac"] = local_hmac
        return json.dumps(payload, sort_keys=True).encode()

    # ── HMAC local ────────────────────────────────────────────────────────────

    def _local_hmac(self, sha256_hex: str, timestamp: int) -> str:
        data = f"{sha256_hex}:{timestamp}".encode()
        return _hmac_module.new(self._key, data, hashlib.sha256).hexdigest()

    # ── API pública ───────────────────────────────────────────────────────────

    def seal_artifact(self, path: str | Path) -> CustodyRecord:
        """
        Sella un artefacto con timestamp RFC 3161.
        Intenta TSAs en orden de prioridad.
        Si todas fallan, usa fallback local declarado explícitamente.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Artefacto no encontrado: {path}")

        ingest_time               = int(time.time())
        sha256_hex, sha512_hex, sz = self._hash_artifact(path)
        tsq                       = self._build_tsq(sha256_hex)

        tsr_bytes   = None
        tsa_used    = None
        independent = False

        for tsa_name in self._prio:
            if tsa_name == "local_hmac":
                tsr_bytes   = self._local_fallback_token(sha256_hex, ingest_time)
                tsa_used    = "local_hmac"
                independent = False
                break
            tsr_bytes = self._send_tsq(tsq, tsa_name)
            if tsr_bytes is not None:
                tsa_used    = tsa_name
                independent = TSA_ENDPOINTS[tsa_name].get("independent", False)
                break

        if tsr_bytes is None:
            tsr_bytes   = self._local_fallback_token(sha256_hex, ingest_time)
            tsa_used    = "local_hmac"
            independent = False

        tsa_policy = TSA_ENDPOINTS.get(tsa_used, {}).get("policy", "unknown")

        record = CustodyRecord(
            artifact_path    = str(path.resolve()),
            artifact_sha256  = sha256_hex,
            artifact_sha512  = sha512_hex,
            artifact_size    = sz,
            ingest_timestamp = ingest_time,
            tsa_name         = tsa_used,
            tsa_token_b64    = base64.b64encode(tsr_bytes).decode("ascii"),
            tsa_timestamp    = ingest_time,   # proxy; verificar con token completo
            tsa_policy       = tsa_policy,
            local_hmac       = self._local_hmac(sha256_hex, ingest_time),
            is_independent   = independent,
            chain_position   = len(self._chain),
        )
        self._chain.append(record)
        return record

    def export_chain(self) -> list[dict]:
        """Exporta la cadena completa para el reporte del bundle."""
        return [
            {
                "position":        r.chain_position,
                "artifact":        r.artifact_path,
                "sha256":          r.artifact_sha256,
                "sha512":          r.artifact_sha512,
                "size_bytes":      r.artifact_size,
                "ingest_utc":      r.ingest_timestamp,
                "tsa":             r.tsa_name,
                "tsa_token_b64":   r.tsa_token_b64,
                "tsa_policy":      r.tsa_policy,
                "is_independent":  r.is_independent,
                "local_hmac":      r.local_hmac,
                "custody_warning": (
                    None if r.is_independent else
                    "LOCAL TIMESTAMP — No independent witness. "
                    "Verify with external TSA before legal use."
                ),
            }
            for r in self._chain
        ]

    def verify_chain_integrity(self) -> dict:
        """Verifica HMAC local de cada registro. No verifica firma TSA."""
        for i, r in enumerate(self._chain):
            expected = self._local_hmac(r.artifact_sha256, r.ingest_timestamp)
            if expected != r.local_hmac:
                return {
                    "valid":     False,
                    "broken_at": i,
                    "details":   f"Chain compromised at position {i}: {r.artifact_path}",
                }
        return {
            "valid":     True,
            "broken_at": None,
            "details":   f"Chain intact: {len(self._chain)} records verified",
        }
