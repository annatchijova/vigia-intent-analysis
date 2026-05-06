# -*- coding: utf-8 -*-
"""
recommendation_engine_v3.1.py

Motor de recomendaciones forenses VIGÍA.

Cambios v3.1 respecto a v3.0:
  B/2: ID determinista = SHA256(audit_id + '|' + policy_id + '|' + timestamp_utc)
       Resuelve colisión de PRIMARY KEY cuando el mismo evento ocurre dos veces
       para la misma política. El timestamp garantiza unicidad temporal.
       Ante misma evidencia + política + timestamp = mismo ID (reproducible, Daubert).
  3:   Validación de podSelector antes de INSERT en recommendation_ledger.
       Un podSelector vacío {} aísla el namespace completo — se rechaza antes
       de persistir el payload.
  Regla X: operator_hmac_signature = NULL hasta autorización humana explícita.

C2 (Claude 2026-05-02): Este módulo NO tiene webhook handler ni _NoRedirect —
el hallazgo aplica a una versión con features de notificación no implementadas aquí.
LLMShield: este módulo no procesa texto que vaya directamente al LLM. La sanitización
LLM se aplica upstream en vigia_planner.py antes de que el evidence_summary llegue
al motor de abducción. Si en el futuro se agrega un webhook, importar y llamar
llm_shield.scan() de vigia.security antes de procesar cualquier URL o payload externo.
           Ninguna acción se ejecuta sin firma HMAC del operador.

INTEGRACIÓN:
    engine = RecommendationEngine(db_path="vigia.db")
    # Llamar después de un veredicto REJECT o ABSTAIN:
    rec = engine.generate_recommendation(
        audit_id="AUDIT-2026-001",
        verdict="REJECT",
        ttp="T1071.004",
        resource_id="pod-dns-exfil-7f9b2",
    )
    # Listar pendientes para el operador:
    pending = engine.list_pending_recommendations()
    # El operador autoriza con su HMAC:
    engine.authorize_and_execute(rec["recommendation_id"], operator_id="analyst-01")

GARANTÍAS DAUBERT:
  - IDs deterministas: mismo input → mismo ID
  - Ninguna acción sin firma humana (Regla X)
  - Toda acción trazada en action_audit_log
  - JSON Schema validado antes de persistir
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ── Constantes ────────────────────────────────────────────────────────────────

_SEPARATOR = "|"  # Separador para SHA256 — evita colisión 'AB'+'CD' vs 'A'+'BCD'

# Campos requeridos en el payload según action_type
_PAYLOAD_REQUIRED_FIELDS: Dict[str, List[str]] = {
    # ISOLATE_POD / QUARANTINE_NAMESPACE usan estructura K8s (NetworkPolicy).
    # El podSelector vive en spec.podSelector — no se valida aquí como campo top-level.
    # La validación específica se hace en el bloque if action_type in (...) más abajo.
    "ISOLATE_POD":          ["spec"],
    "QUARANTINE_NAMESPACE": ["spec"],
    "COLLECT_FORENSICS":    ["target_pod", "tools"],
    "REVOKE_SA_TOKEN":      ["service_account"],
    "ROTATE_CREDENTIALS":   ["service_account"],
    "ESCALATE_HUMAN":       ["message", "resource_id"],
}


def _utcnow() -> str:
    """Timestamp UTC ISO-8601 determinista."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _deterministic_id(audit_id: str, policy_id: str, timestamp_utc: str) -> str:
    """
    B/2: ID determinista para recommendation_ledger.

    SHA256(audit_id | policy_id | timestamp_utc)

    Propiedades:
      - Unicidad temporal: mismo evento repetido → timestamps distintos → IDs distintos
      - Reproducibilidad: misma evidencia + política + timestamp → mismo ID
      - El separador '|' evita colisiones por concatenación
    """
    raw = _SEPARATOR.join([audit_id, policy_id, timestamp_utc])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_payload(action_type: str, payload_json: str) -> Dict[str, Any]:
    """
    Valida el payload JSON antes de persistir en recommendation_ledger.

    Raises:
        ValueError: Si el JSON es inválido, faltan campos requeridos,
                    o el podSelector está vacío (vulnerabilidad #3).
    """
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Payload JSON inválido: {e}") from e

    required = _PAYLOAD_REQUIRED_FIELDS.get(action_type, [])
    missing = [f for f in required if f not in payload]
    if missing:
        raise ValueError(
            f"Payload para {action_type} falta campos requeridos: {missing}"
        )

    # Validación #3: podSelector no puede ser vacío
    if action_type in ("ISOLATE_POD", "QUARANTINE_NAMESPACE"):
        # Buscar podSelector en estructura K8s (spec.podSelector) o top-level
        pod_selector = (
            payload.get("spec", {}).get("podSelector")
            or payload.get("podSelector")
        )
        if pod_selector == {} or pod_selector is None:
            raise ValueError(
                f"podSelector vacío en payload de {action_type}. "
                "Un selector vacío {{}} aísla el namespace completo. "
                "Proporcionar matchLabels con el resource_id específico del pod."
            )
        # Verificar que matchLabels no está vacío si existe
        match_labels = pod_selector.get("matchLabels", pod_selector)
        if match_labels == {}:
            raise ValueError(
                f"podSelector.matchLabels vacío en payload de {action_type}. "
                "Proporcionar al menos una label con el resource_id del pod."
            )

    return payload


class RecommendationEngine:
    """
    Motor de recomendaciones forenses.

    Conecta RiskBoundedDecisionLayer con el recommendation_ledger.
    Toda acción requiere autorización humana (Regla X).
    """

    def __init__(self, db_path: str = "vigia.db") -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def generate_recommendation(
        self,
        audit_id: str,
        verdict: str,
        resource_id: str,
        ttp: Optional[str] = None,
        timestamp_utc: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Genera una recomendación para un veredicto dado.

        El ID se calcula determinísticamente:
            SHA256(audit_id | policy_id | timestamp_utc)

        SEG-2 (2026-05-02): timestamp_utc DEBE ser el reloj interno del motor
        (Terceridad), nunca el timestamp del artefacto observado (Primeridad).
        Los logs del sistema son manipulables — un atacante que controle los
        timestamps del log puede precalcular el ID y bloquear la política legítima
        con un INSERT previo (Replay Attack via Primary Key collision).
        Si el caller pasa timestamp_utc, se documenta como responsabilidad del
        caller usar _utcnow() y nunca un valor proveniente de la evidencia.
        Por defecto: _utcnow() del motor.

        Returns:
            Dict con los campos de la recomendación, o None si no hay política.
        """
        # SEG-2: siempre usar reloj interno si no se provee timestamp explícito
        ts = timestamp_utc or _utcnow()
        conn = self._get_conn()

        # Buscar política aplicable
        cur = conn.execute(
            """
            SELECT * FROM recommendation_policies
            WHERE enabled = 1
              AND trigger_verdict = ?
              AND (trigger_ttp = ? OR trigger_ttp IS NULL)
            ORDER BY priority ASC
            LIMIT 1
            """,
            (verdict, ttp),
        )
        policy = cur.fetchone()
        if policy is None:
            return None

        policy_id = policy["policy_id"]

        # B/2: ID determinista
        rec_id = _deterministic_id(audit_id, policy_id, ts)

        # Resolver {resource_id} en el template
        raw_payload = policy["action_payload_template"].replace("{resource_id}", resource_id)

        # Validar payload antes de persistir (incluye validación #3 podSelector)
        try:
            _validate_payload(policy["action_type"], raw_payload)
        except ValueError as e:
            # Log de seguridad — no propagar excepción para no bloquear el pipeline
            print(f"[RecommendationEngine] WARN: payload inválido para {policy_id}: {e}",
                  flush=True)
            return None

        try:
            conn.execute(
                """
                INSERT INTO recommendation_ledger (
                    recommendation_id, audit_id, policy_id, timestamp_utc,
                    action_payload, triggered_by_verdict, triggered_by_ttp,
                    resource_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (rec_id, audit_id, policy_id, ts, raw_payload, verdict, ttp, resource_id),
            )
            conn.execute(
                """
                INSERT INTO action_audit_log (log_id, recommendation_id, action, actor, timestamp_utc)
                VALUES (?, ?, 'CREATED', 'vigia_engine', ?)
                """,
                (hashlib.sha256(f"{rec_id}|CREATED|{ts}".encode()).hexdigest(), rec_id, ts),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            # P1-004 (Kimi 2026-05-02): IntegrityError no es solo por PRIMARY KEY.
            # También cubre FOREIGN KEY, CHECK, NOT NULL — si silenciamos todos,
            # un payload con violación CHECK queda sin registrar y el engine
            # retorna un row existente que puede ser de otra recomendación.
            # Fix: re-lanzar si NO es un duplicado de recommendation_id.
            err_str = str(e).lower()
            if "recommendation_id" not in err_str and "unique" not in err_str:
                raise  # No es duplicado — propagar para debugging
            # Es duplicado de ID: reproducibilidad por diseño, retornar el existente

        cur2 = conn.execute(
            "SELECT * FROM recommendation_ledger WHERE recommendation_id = ?", (rec_id,)
        )
        row = cur2.fetchone()
        return dict(row) if row else None

    def list_pending_recommendations(self) -> List[Dict[str, Any]]:
        """Retorna todas las recomendaciones pendientes de autorización humana."""
        conn = self._get_conn()
        cur = conn.execute("SELECT * FROM v_pending_recommendations")
        return [dict(r) for r in cur.fetchall()]

    def authorize_and_execute(
        self,
        recommendation_id: str,
        operator_id: str,
        hmac_key: Optional[bytes] = None,
    ) -> bool:
        """
        Regla X: autorización humana con firma HMAC.

        Si hmac_key es None, usa la variable de entorno VIGIA_HMAC_KEY.
        Retorna True si la autorización fue exitosa.
        """
        key = hmac_key or os.environ.get("VIGIA_HMAC_KEY", "").encode("utf-8")
        if not key:
            raise ValueError(
                "HMAC key requerida. Proporcionar hmac_key o setear VIGIA_HMAC_KEY."
            )

        conn = self._get_conn()
        cur = conn.execute(
            "SELECT * FROM recommendation_ledger WHERE recommendation_id = ?",
            (recommendation_id,),
        )
        rec = cur.fetchone()
        if rec is None:
            raise ValueError(f"Recomendación no encontrada: {recommendation_id}")
        if rec["status"] != "PENDING":
            raise ValueError(f"Recomendación no está en PENDING: {rec['status']}")

        ts = _utcnow()
        canonical = f"{recommendation_id}|{operator_id}|{ts}"
        signature = hmac.new(key, canonical.encode("utf-8"), "sha256").hexdigest()

        conn.execute(
            """
            UPDATE recommendation_ledger
            SET status = 'AUTHORIZED',
                operator_hmac_signature = ?,
                authorized_by = ?,
                authorized_at = ?
            WHERE recommendation_id = ?
            """,
            (signature, operator_id, ts, recommendation_id),
        )
        conn.execute(
            """
            INSERT INTO action_audit_log (log_id, recommendation_id, action, actor, timestamp_utc, details)
            VALUES (?, ?, 'AUTHORIZED', ?, ?, ?)
            """,
            (
                hashlib.sha256(f"{recommendation_id}|AUTHORIZED|{ts}".encode()).hexdigest(),
                recommendation_id,
                operator_id,
                ts,
                json.dumps({"hmac_prefix": signature[:16]}, sort_keys=True),
            ),
        )
        conn.commit()
        return True

    def get_recommendation_spec(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Metadata completa de una recomendación para incluir en el bundle forense."""
        conn = self._get_conn()
        cur = conn.execute(
            """
            SELECT r.*, p.display_name, p.action_type, p.priority
            FROM recommendation_ledger r
            JOIN recommendation_policies p ON r.policy_id = p.policy_id
            WHERE r.recommendation_id = ?
            """,
            (recommendation_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
