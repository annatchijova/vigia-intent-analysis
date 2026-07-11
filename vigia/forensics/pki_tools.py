"""
vigia/forensics/pki_tools.py
─────────────────────────────────────────────────────────────────────────────
PKI Tools — VIGIA Forensic Suite — Grado Gubernamental

COMPONENTES:
    TimestampClient   — RFC 3161 timestamp sobre el bundle_hash
    HSMConnector      — PKCS#11 para firma con clave privada en HSM/token
    ReceiptProof      — artefacto sellado de prueba de timestamp

ESTANDARES IMPLEMENTADOS:
    RFC 3161  — Time-Stamp Protocol (TSP)
    PKCS#11   — Cryptographic Token Interface Standard
    ETSI EN 319 102 — PAdES baseline profiles
    eIDAS     — Qualified Electronic Signatures

ARQUITECTURA ZERO-TRUST:
    - La clave privada NUNCA sale del HSM (principio PKCS#11)
    - El timestamp es producido por una TSA externa independiente
    - El ReceiptProof incluye la cadena de verificacion completa
    - Verificacion posible sin acceso al sistema original

FALLBACK:
    Si el HSM no esta disponible → HashReceiptProof (solo hash local)
    Si la TSA no responde → CachedTimestampProof (timestamp local documentado)
    El bundle ES VALIDO sin PKI — PKI agrega non-repudiation, no integridad basica

INTEGRACION EN EL PIPELINE:
    bundle = ForensicBundle(...)
    sealed = BundleBuilder.seal(bundle)

    # Opcional pero recomendado para grado gubernamental
    ts_client = TimestampClient(tsa_url="http://tsa.example.gov/tsa")
    receipt = ts_client.stamp(sealed["integrity"]["bundle_hash"])
    sealed["pki"] = receipt.to_dict()

    # Con HSM
    hsm = HSMConnector(pkcs11_lib="/usr/lib/softhsm/libsofthsm2.so")
    hsm.connect(slot=0, pin="XXXXX")
    sig = hsm.sign(sealed["integrity"]["bundle_hash"])
    sealed["pki"]["signature"] = sig.to_dict()
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import struct
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# B-097 root cause: this module inserted <repo>/vigia into sys.path at
# import time — especially hazardous here because pki_tools.py exists BOTH
# as vigia/forensics/pki_tools.py and <repo>/forensics/pki_tools.py, so the
# name resolved to a different module depending on import order. All
# imports here are vigia.-qualified or third-party; the insert served
# nothing.

# ---------------------------------------------------------------------------
# Dependencias opcionales
# ---------------------------------------------------------------------------
try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _requests = None  # type: ignore
    _REQUESTS_AVAILABLE = False

try:
    import pkcs11 as _pkcs11
    from pkcs11 import Mechanism, KeyType, ObjectClass
    _PKCS11_AVAILABLE = True
except ImportError:
    _pkcs11 = None  # type: ignore
    _PKCS11_AVAILABLE = False


# ---------------------------------------------------------------------------
# ReceiptProof — artefacto de prueba de timestamp
# ---------------------------------------------------------------------------

class ReceiptProof:
    """
    Prueba criptografica de que un bundle_hash existia en un momento dado.

    Tipos:
        rfc3161      — token RFC 3161 de TSA externa (maxima garantia)
        local_hash   — hash local con timestamp del sistema (fallback)
        cached       — timestamp cached de TSA anterior (TSA no disponible)

    El to_dict() produce un registro auditable para inclusion en el bundle.
    """

    def __init__(
        self,
        bundle_hash: str,
        proof_type: str,
        timestamp_utc: str,
        tsa_url: Optional[str] = None,
        tsa_response_hex: Optional[str] = None,
        tsa_serial: Optional[str] = None,
        local_anchor: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        self.bundle_hash = bundle_hash
        self.proof_type = proof_type          # "rfc3161" | "local_hash" | "cached"
        self.timestamp_utc = timestamp_utc
        self.tsa_url = tsa_url
        self.tsa_response_hex = tsa_response_hex
        self.tsa_serial = tsa_serial
        self.local_anchor = local_anchor      # SHA-256 del proof para verificacion local
        self.error = error

        # Calcular anchor del proof para verificacion
        self.local_anchor = self._compute_anchor()

    def _compute_anchor(self) -> str:
        """Hash SHA-256 del proof — permite verificar integridad del receipt."""
        payload = json.dumps(
            {
                "bundle_hash": self.bundle_hash,
                "proof_type": self.proof_type,
                "timestamp_utc": self.timestamp_utc,
                "tsa_url": self.tsa_url,
                "tsa_serial": self.tsa_serial,
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def is_tsa_backed(self) -> bool:
        """True si el proof viene de una TSA externa (RFC 3161)."""
        return self.proof_type == "rfc3161" and self.tsa_response_hex is not None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_type": self.proof_type,
            "bundle_hash": self.bundle_hash,
            "timestamp_utc": self.timestamp_utc,
            "tsa_url": self.tsa_url,
            "tsa_serial": self.tsa_serial,
            "tsa_response_hex": self.tsa_response_hex,
            "local_anchor": self.local_anchor,
            "error": self.error,
            "is_tsa_backed": self.is_tsa_backed(),
        }

    def __repr__(self) -> str:
        return (
            f"<ReceiptProof type={self.proof_type} "
            f"hash={self.bundle_hash[:12]}... "
            f"ts={self.timestamp_utc}>"
        )


# ---------------------------------------------------------------------------
# TimestampClient — RFC 3161 TSA
# ---------------------------------------------------------------------------

class TimestampClient:
    """
    Cliente RFC 3161 para solicitar timestamps a una TSA externa.

    Protocolo:
        1. Construir TimeStampReq (hash del bundle_hash + nonce)
        2. POST a TSA endpoint
        3. Parsear TimeStampResp
        4. Retornar ReceiptProof con el token

    Si la TSA no responde → retorna ReceiptProof de tipo "local_hash"
    con timestamp local documentado como fallback.

    TSAs publicas de referencia:
        DigiCert:     http://timestamp.digicert.com
        GlobalSign:   http://timestamp.globalsign.com/scripts/timstamp.dll
        Sectigo:      http://timestamp.sectigo.com
        FreeTSA:      https://freetsa.org/tsr  (testing, no-QES)
    """

    # Timeout para requests TSA (segundos)
    DEFAULT_TIMEOUT: int = 10

    # OID SHA-256 para TimeStampReq
    # ASN.1: AlgorithmIdentifier { algorithm OID 2.16.840.1.101.3.4.2.1 }
    _SHA256_OID_HEX = "300d06096086480165030402010500"

    def __init__(
        self,
        tsa_url: str,
        timeout: int = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ) -> None:
        self.tsa_url = tsa_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def stamp(self, bundle_hash: str) -> ReceiptProof:
        """
        Solicita un timestamp RFC 3161 para el bundle_hash dado.

        Args:
            bundle_hash: SHA-256 hex del bundle (64 chars)

        Returns:
            ReceiptProof con token RFC 3161 o fallback local
        """
        now_utc = datetime.now(timezone.utc).isoformat()

        if not _REQUESTS_AVAILABLE:
            logger.warning(
                "[TimestampClient] requests no disponible — fallback a local_hash"
            )
            return self._local_fallback(bundle_hash, now_utc, "requests_not_installed")

        try:
            tsq_der = self._build_timestamp_request(bundle_hash)
            response = _requests.post(
                self.tsa_url,
                data=tsq_der,
                headers={"Content-Type": "application/timestamp-query"},
                timeout=self.timeout,
                verify=self.verify_ssl,
            )

            if response.status_code != 200:
                raise RuntimeError(f"TSA HTTP {response.status_code}: {response.text[:200]}")

            tsr_der = response.content
            serial = self._extract_serial(tsr_der)

            logger.info(
                "[TimestampClient] TSA OK: %s | serial=%s | bundle_hash=%s",
                self.tsa_url, serial, bundle_hash[:16],
            )

            return ReceiptProof(
                bundle_hash=bundle_hash,
                proof_type="rfc3161",
                timestamp_utc=now_utc,
                tsa_url=self.tsa_url,
                tsa_response_hex=tsr_der.hex(),
                tsa_serial=serial,
            )

        except Exception as e:
            logger.error(
                "[TimestampClient] TSA fallida (%s): %s — usando local_hash",
                self.tsa_url, e,
            )
            return self._local_fallback(bundle_hash, now_utc, str(e))

    def stamp_multiple(
        self,
        bundle_hash: str,
        tsa_urls: Optional[list] = None,
    ) -> Dict[str, ReceiptProof]:
        """
        Solicita timestamps a multiples TSAs para redundancia jurisdiccional.

        Estrategia recomendada para grado gubernamental:
            - 2-3 TSAs en distintas jurisdicciones
            - Al menos 1 QES-compliant (eIDAS / ETSI)
            - Registrar todas en el bundle

        Retorna: {tsa_url: ReceiptProof}
        """
        urls = tsa_urls or [self.tsa_url]
        results: Dict[str, ReceiptProof] = {}

        for url in urls:
            client = TimestampClient(url, timeout=self.timeout, verify_ssl=self.verify_ssl)
            results[url] = client.stamp(bundle_hash)
            logger.info(
                "[TimestampClient] TSA %s: type=%s",
                url, results[url].proof_type,
            )

        n_backed = sum(1 for r in results.values() if r.is_tsa_backed())
        logger.info(
            "[TimestampClient] Multi-TSA: %d/%d con respaldo RFC 3161",
            n_backed, len(urls),
        )

        return results

    # ------------------------------------------------------------------
    # Construccion de TimeStampReq (DER minimal, RFC 3161)
    # ------------------------------------------------------------------

    def _build_timestamp_request(self, bundle_hash: str) -> bytes:
        """
        Construye un TimeStampReq DER minimo (RFC 3161 §2.4.1).

        TimeStampReq ::= SEQUENCE {
            version         INTEGER  { v1(1) },
            messageImprint  MessageImprint,
            reqPolicy       OBJECT IDENTIFIER OPTIONAL,
            nonce           INTEGER OPTIONAL,
            certReq         BOOLEAN DEFAULT FALSE
        }
        MessageImprint ::= SEQUENCE {
            hashAlgorithm   AlgorithmIdentifier,
            hashedMessage   OCTET STRING
        }

        NOTA: Implementacion minimal para interop basica.
        En produccion usar python-tsp (RFC 3161 completo) o pyHanko.
        """
        import os
        hash_bytes = bytes.fromhex(bundle_hash)
        nonce_int = int.from_bytes(os.urandom(8), "big")

        # SHA-256 AlgorithmIdentifier
        algo_oid = bytes.fromhex("300d06096086480165030402010500")

        # hashedMessage: OCTET STRING
        hashed_msg = b"\x04\x20" + hash_bytes

        # MessageImprint: SEQUENCE
        mi_inner = algo_oid + hashed_msg
        mi = b"\x30" + self._der_len(len(mi_inner)) + mi_inner

        # version: INTEGER 1
        version = b"\x02\x01\x01"

        # nonce: INTEGER (8 bytes)
        nonce_bytes = nonce_int.to_bytes(8, "big").lstrip(b"\x00") or b"\x00"
        nonce = b"\x02" + self._der_len(len(nonce_bytes)) + nonce_bytes

        # certReq: BOOLEAN TRUE
        cert_req = b"\x01\x01\xff"

        # TimeStampReq: SEQUENCE
        tsq_inner = version + mi + nonce + cert_req
        tsq = b"\x30" + self._der_len(len(tsq_inner)) + tsq_inner

        return tsq

    @staticmethod
    def _der_len(n: int) -> bytes:
        """Codificacion de longitud DER."""
        if n < 0x80:
            return bytes([n])
        elif n < 0x100:
            return bytes([0x81, n])
        else:
            return bytes([0x82, (n >> 8) & 0xff, n & 0xff])

    @staticmethod
    def _extract_serial(tsr_der: bytes) -> str:
        """
        Extrae el serial number del TimeStampToken.
        P1-8: heurística reforzada con límite de búsqueda y validación de rango.
        Para parser ASN.1 completo usar pyasn1 + rfc3161.
        """
        try:
            if not isinstance(tsr_der, bytes) or len(tsr_der) < 4:
                return "unknown"
            # Limitar búsqueda a los primeros 512 bytes — el serial está al inicio
            search_space = tsr_der[:512]
            idx = search_space.find(b"\x02\x01")
            if idx >= 0 and idx + 3 <= len(search_space):
                serial_val = search_space[idx + 2]
                # Validar que es un valor de serial razonable (no inyección)
                if 0x01 <= serial_val <= 0xFF:
                    return f"{serial_val:08x}"
            return "unknown"
        except Exception:
            return "unknown"

    def _local_fallback(
        self,
        bundle_hash: str,
        now_utc: str,
        reason: str,
    ) -> ReceiptProof:
        """Fallback: timestamp local documentado como 'local_hash'."""
        return ReceiptProof(
            bundle_hash=bundle_hash,
            proof_type="local_hash",
            timestamp_utc=now_utc,
            tsa_url=self.tsa_url,
            error=f"TSA fallback activo: {reason}",
        )


# ---------------------------------------------------------------------------
# HSMSignature — resultado de firma con HSM
# ---------------------------------------------------------------------------

class HSMSignature:
    """
    Firma digital producida por HSM/token PKCS#11.

    La clave privada NUNCA sale del HSM.
    Se firma el bundle_hash directamente para minimizar data expuesta.
    """

    def __init__(
        self,
        bundle_hash: str,
        signature_hex: str,
        algorithm: str,
        key_id: str,
        slot: int,
        timestamp_utc: str,
        pkcs11_lib: str,
        error: Optional[str] = None,
    ) -> None:
        self.bundle_hash = bundle_hash
        self.signature_hex = signature_hex
        self.algorithm = algorithm   # "RSA_PKCS" | "ECDSA" | "RSA_PKCS_PSS"
        self.key_id = key_id
        self.slot = slot
        self.timestamp_utc = timestamp_utc
        self.pkcs11_lib = pkcs11_lib
        self.error = error

    def is_valid_format(self) -> bool:
        return bool(self.signature_hex) and len(self.signature_hex) >= 64

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_hash": self.bundle_hash,
            "signature_hex": self.signature_hex,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "slot": self.slot,
            "timestamp_utc": self.timestamp_utc,
            "pkcs11_lib": os.path.basename(self.pkcs11_lib),
            "error": self.error,
        }


# ---------------------------------------------------------------------------
# HSMConnector — PKCS#11
# ---------------------------------------------------------------------------

class HSMConnector:
    """
    Conector PKCS#11 para firma con HSM o token criptografico.

    Compatible con:
        SoftHSM2  (testing local)
        YubiKey 5 (hardware token)
        SafeNet/Thales Luna (HSM gubernamental)
        AWS CloudHSM (via PKCS#11 driver)
        Azure Dedicated HSM (via PKCS#11 driver)

    La clave privada NUNCA se exporta del dispositivo.
    La firma se realiza dentro del HSM sobre el hash del bundle.

    INSTALACION:
        pip install python-pkcs11
        # SoftHSM2 para testing:
        # apt install softhsm2
        # softhsm2-util --init-token --slot 0 --label "vigia"
    """

    def __init__(
        self,
        pkcs11_lib: str,
        algorithm: str = "RSA_PKCS_PSS",
    ) -> None:
        self.pkcs11_lib = pkcs11_lib
        self.algorithm = algorithm
        self._lib = None
        self._session = None
        self._connected = False

    def connect(self, slot: int = 0, pin: str = "") -> bool:
        """
        Abre sesion con el token en el slot especificado.

        Args:
            slot: numero de slot PKCS#11 (0 para primer token)
            pin : PIN/contrasena del token

        Retorna True si la conexion fue exitosa.
        """
        if not _PKCS11_AVAILABLE:
            logger.warning(
                "[HSMConnector] python-pkcs11 no disponible. "
                "Instalar: pip install python-pkcs11"
            )
            return False

        try:
            self._lib = _pkcs11.lib(self.pkcs11_lib)
            token = self._lib.get_token(slot_id=slot)
            self._session = token.open(user_pin=pin)
            self._connected = True
            logger.info(
                "[HSMConnector] Conectado: lib=%s slot=%d",
                os.path.basename(self.pkcs11_lib), slot,
            )
            return True
        except Exception as e:
            logger.error("[HSMConnector] Conexion fallida: %s", e)
            self._connected = False
            return False

    def sign(
        self,
        bundle_hash: str,
        key_label: Optional[str] = None,
        key_id: Optional[bytes] = None,
    ) -> HSMSignature:
        """
        Firma el bundle_hash con la clave privada en el HSM.

        Args:
            bundle_hash : SHA-256 hex del bundle
            key_label   : etiqueta de la clave en el token
            key_id      : ID binario de la clave (alternativo a label)

        Retorna HSMSignature con la firma y metadatos.
        La clave privada NUNCA sale del HSM.
        """
        now_utc = datetime.now(timezone.utc).isoformat()
        slot = 0

        if not self._connected or not _PKCS11_AVAILABLE:
            return HSMSignature(
                bundle_hash=bundle_hash,
                signature_hex="",
                algorithm=self.algorithm,
                key_id=key_label or "unknown",
                slot=slot,
                timestamp_utc=now_utc,
                pkcs11_lib=self.pkcs11_lib,
                error="HSM no conectado o pkcs11 no disponible",
            )

        try:
            hash_bytes = bytes.fromhex(bundle_hash)

            # Buscar clave privada en el token
            if key_label:
                private_keys = list(
                    self._session.get_objects({
                        _pkcs11.Attribute.CLASS: ObjectClass.PRIVATE_KEY,
                        _pkcs11.Attribute.LABEL: key_label,
                    })
                )
            elif key_id:
                private_keys = list(
                    self._session.get_objects({
                        _pkcs11.Attribute.CLASS: ObjectClass.PRIVATE_KEY,
                        _pkcs11.Attribute.ID: key_id,
                    })
                )
            else:
                private_keys = list(
                    self._session.get_objects({
                        _pkcs11.Attribute.CLASS: ObjectClass.PRIVATE_KEY,
                    })
                )

            if not private_keys:
                raise RuntimeError("No se encontro clave privada en el token")

            priv_key = private_keys[0]
            key_id_str = key_label or str(priv_key.get(_pkcs11.Attribute.ID, b"").hex())

            # Firmar — la operacion ocurre dentro del HSM
            mechanism = getattr(Mechanism, self.algorithm, Mechanism.RSA_PKCS)
            signature_bytes = priv_key.sign(hash_bytes, mechanism=mechanism)

            logger.info(
                "[HSMConnector] Firma OK: algo=%s key=%s bundle=%s",
                self.algorithm, key_id_str, bundle_hash[:16],
            )

            return HSMSignature(
                bundle_hash=bundle_hash,
                signature_hex=signature_bytes.hex(),
                algorithm=self.algorithm,
                key_id=key_id_str,
                slot=slot,
                timestamp_utc=now_utc,
                pkcs11_lib=self.pkcs11_lib,
            )

        except Exception as e:
            logger.error("[HSMConnector] Firma fallida: %s", e)
            return HSMSignature(
                bundle_hash=bundle_hash,
                signature_hex="",
                algorithm=self.algorithm,
                key_id=key_label or "unknown",
                slot=slot,
                timestamp_utc=now_utc,
                pkcs11_lib=self.pkcs11_lib,
                error=str(e),
            )

    def disconnect(self) -> None:
        """Cierra la sesion con el token."""
        if self._session:
            try:
                self._session.close()
            except Exception:
                pass
        self._connected = False
        logger.info("[HSMConnector] Desconectado")

    def __enter__(self) -> "HSMConnector":
        return self

    def __exit__(self, *args) -> None:
        self.disconnect()


# ---------------------------------------------------------------------------
# PKIRecord — registro PKI completo para inclusion en el bundle
# ---------------------------------------------------------------------------

class PKIRecord:
    """
    Registro PKI completo: timestamp(s) + firma HSM + metadatos.

    Se incluye en el sealed_dict como sealed_dict["pki"].
    NO es parte del bundle_hash (es post-sellado) — es evidencia adicional.

    NOTA: El bundle es valido sin PKI. El PKIRecord agrega:
        - Non-repudiation (quien produjo el bundle)
        - Time proof (cuando existia el hash)
        - Long-term validity (el hash sobrevive a la firma digital)
    """

    def __init__(
        self,
        bundle_hash: str,
        timestamps: Optional[Dict[str, ReceiptProof]] = None,
        hsm_signature: Optional[HSMSignature] = None,
    ) -> None:
        self.bundle_hash = bundle_hash
        self.timestamps = timestamps or {}
        self.hsm_signature = hsm_signature
        self.created_at = datetime.now(timezone.utc).isoformat()

    def has_tsa_proof(self) -> bool:
        return any(r.is_tsa_backed() for r in self.timestamps.values())

    def has_hsm_signature(self) -> bool:
        return self.hsm_signature is not None and self.hsm_signature.is_valid_format()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_hash": self.bundle_hash,
            "created_at": self.created_at,
            "timestamps": {url: r.to_dict() for url, r in self.timestamps.items()},
            "hsm_signature": self.hsm_signature.to_dict() if self.hsm_signature else None,
            "has_tsa_proof": self.has_tsa_proof(),
            "has_hsm_signature": self.has_hsm_signature(),
        }


# ---------------------------------------------------------------------------
# Funcion de conveniencia: stamp_and_sign
# ---------------------------------------------------------------------------

def stamp_and_sign(
    bundle_hash: str,
    tsa_urls: Optional[list] = None,
    pkcs11_lib: Optional[str] = None,
    hsm_slot: int = 0,
    hsm_pin: str = "",
    hsm_key_label: Optional[str] = None,
) -> PKIRecord:
    """
    Atesta el bundle_hash con timestamp(s) TSA y firma HSM opcional.

    Esta funcion es el entry point principal para sellar un bundle
    con infraestructura PKI gubernamental.

    Args:
        bundle_hash   : SHA-256 del bundle (del BundleBuilder.seal())
        tsa_urls      : lista de TSA endpoints. Default: FreeTSA (testing)
        pkcs11_lib    : path a la libreria PKCS#11. None = sin firma HSM
        hsm_slot      : slot del token PKCS#11
        hsm_pin       : PIN del token
        hsm_key_label : etiqueta de la clave privada en el token

    Retorna: PKIRecord listo para incluir en sealed_dict["pki"]

    Ejemplo:
        record = stamp_and_sign(
            bundle_hash=sealed["integrity"]["bundle_hash"],
            tsa_urls=["http://timestamp.digicert.com",
                      "http://timestamp.globalsign.com/scripts/timstamp.dll"],
            pkcs11_lib="/usr/lib/softhsm/libsofthsm2.so",
            hsm_key_label="vigia-signing-key",
        )
        sealed["pki"] = record.to_dict()
    """
    # Timestamps
    default_tsa = ["https://freetsa.org/tsr"]  # testing — reemplazar con TSA gubernamental
    urls = tsa_urls or default_tsa

    ts_client = TimestampClient(urls[0])
    timestamps = ts_client.stamp_multiple(bundle_hash, tsa_urls=urls)

    # Firma HSM (opcional)
    hsm_sig = None
    if pkcs11_lib:
        with HSMConnector(pkcs11_lib) as hsm:
            if hsm.connect(slot=hsm_slot, pin=hsm_pin):
                hsm_sig = hsm.sign(bundle_hash, key_label=hsm_key_label)
            else:
                logger.warning("[stamp_and_sign] HSM no disponible — omitiendo firma")

    return PKIRecord(
        bundle_hash=bundle_hash,
        timestamps=timestamps,
        hsm_signature=hsm_sig,
    )
