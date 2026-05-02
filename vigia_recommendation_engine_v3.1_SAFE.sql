-- =============================================================================
-- VIGÍA — vigia_recommendation_engine_v3.1_SAFE.sql
--
-- Motor de recomendaciones forenses con:
--   B/2: ID determinista = SHA256(audit_id || policy_id || timestamp_utc)
-- P2-004 (Kimi 2026-05-02): strftime('now') usa el reloj del SO.
-- Si el servidor no está en UTC, los timestamps llevarán sufijo 'Z' incorrecto.
-- REQUISITO: el servidor SIFT debe tener TZ=UTC. Verificar con: date -u
-- Alternativa: insertar políticas desde Python usando _utcnow() del engine,
-- que garantiza UTC independientemente del TZ del SO.
-- Para SQLite: strftime('%Y-%m-%dT%H:%M:%SZ', 'now') es UTC solo si el SO lo es.
--        Garantiza unicidad temporal sin colisión por eventos repetidos.
--        Un mismo ataque repetido genera IDs distintos (timestamp diferente).
--        Ante la misma evidencia + política + timestamp = mismo ID (reproducible).
--   3:   Validación de podSelector específico (no vacío) antes de INSERT.
--        Previene NetworkPolicy que aísle namespace completo.
--   Regla X: operator_hmac_signature DEFAULT NULL (firma humana obligatoria).
--   Sin triggers automáticos — llamar desde Python vía RecommendationEngine.
--   Sin dependencia de witness_audit_log (tabla inexistente en v3.0).
--
-- Autor: Colectivo VIGÍA (Claude — integrador, Kimi — auditoría, Gemini — diseño)
-- Versión: 3.1
-- Fecha: 2026-05-02
-- =============================================================================

-- ── Tablas ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS recommendation_policies (
    policy_id           TEXT    PRIMARY KEY,
    display_name        TEXT    NOT NULL,
    -- Condición de activación: verdict que dispara esta política
    trigger_verdict     TEXT    NOT NULL CHECK (trigger_verdict IN ('REJECT', 'ABSTAIN', 'ESCALATE')),
    -- TTP MITRE que activa esta política (NULL = aplica a cualquier TTP)
    trigger_ttp         TEXT,
    -- Tipo de acción a recomendar
    action_type         TEXT    NOT NULL CHECK (action_type IN (
                            'ISOLATE_POD', 'ROTATE_CREDENTIALS', 'COLLECT_FORENSICS',
                            'ESCALATE_HUMAN', 'QUARANTINE_NAMESPACE', 'REVOKE_SA_TOKEN'
                        )),
    -- Template del payload JSON de acción.
    -- SEGURIDAD: Este campo es texto plano. El Python que lo use DEBE
    -- validar contra JSON Schema antes de enviar a cualquier API.
    -- {resource_id} se reemplaza por el ID real del pod/recurso afectado.
    action_payload_template TEXT NOT NULL,
    -- Prioridad de escalamiento (1=crítico, 5=informativo)
    priority            INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    enabled             INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
    created_at          TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);


CREATE TABLE IF NOT EXISTS recommendation_ledger (
    -- B/2: ID DETERMINISTA = lower(hex(sha256(audit_id || '|' || policy_id || '|' || timestamp_utc)))
    -- Unicidad temporal: mismo ataque repetido → timestamps distintos → IDs distintos (no colisión)
    -- Reproducibilidad: misma evidencia + política + timestamp → mismo ID (Daubert)
    -- El separador '|' evita colisiones por concatenación: 'AB'+'CD' ≠ 'A'+'BCD'
    recommendation_id   TEXT    PRIMARY KEY,
    audit_id            TEXT    NOT NULL,
    policy_id           TEXT    NOT NULL REFERENCES recommendation_policies(policy_id),
    timestamp_utc       TEXT    NOT NULL,
    -- Payload resuelto: {resource_id} ya sustituido por el ID real del pod
    -- VALIDACIÓN OBLIGATORIA: el Python que inserta aquí debe verificar:
    --   1. JSON válido (json.loads sin excepción)
    --   2. Si action_type='ISOLATE_POD': podSelector no vacío ({})
    --   3. Si action_type='QUARANTINE_NAMESPACE': confirmación humana required
    action_payload      TEXT    NOT NULL,
    -- Veredicto que disparó esta recomendación
    triggered_by_verdict TEXT   NOT NULL,
    -- TTP MITRE observado
    triggered_by_ttp    TEXT,
    -- ID del recurso afectado (pod, SA, namespace)
    resource_id         TEXT    NOT NULL,
    -- Estado del ciclo de vida
    status              TEXT    NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('PENDING', 'AUTHORIZED', 'EXECUTED', 'REJECTED', 'EXPIRED')),
    -- Regla X: firma HMAC del operador humano (NULL hasta autorización)
    -- Ninguna acción puede ejecutarse con operator_hmac_signature = NULL
    operator_hmac_signature TEXT DEFAULT NULL,
    authorized_by       TEXT,
    authorized_at       TEXT,
    executed_at         TEXT,
    notes               TEXT
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_rec_ledger_status
    ON recommendation_ledger(status, timestamp_utc DESC);

CREATE INDEX IF NOT EXISTS idx_rec_ledger_audit
    ON recommendation_ledger(audit_id);

CREATE INDEX IF NOT EXISTS idx_rec_ledger_policy
    ON recommendation_ledger(policy_id, status);


CREATE TABLE IF NOT EXISTS action_audit_log (
    log_id          TEXT    PRIMARY KEY,
    recommendation_id TEXT  NOT NULL REFERENCES recommendation_ledger(recommendation_id),
    action          TEXT    NOT NULL CHECK (action IN (
                        'CREATED', 'AUTHORIZED', 'EXECUTED', 'REJECTED',
                        'EXPIRED', 'ESCALATED', 'HMAC_VERIFIED', 'HMAC_FAILED'
                    )),
    actor           TEXT    NOT NULL,
    timestamp_utc   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    details         TEXT
);

-- ── Vista de recomendaciones pendientes ──────────────────────────────────────

CREATE VIEW IF NOT EXISTS v_pending_recommendations AS
SELECT
    r.recommendation_id,
    r.audit_id,
    p.display_name      AS policy_name,
    p.action_type,
    r.resource_id,
    r.triggered_by_verdict,
    r.triggered_by_ttp,
    r.timestamp_utc,
    p.priority,
    -- Indicador de seguridad: si el podSelector está vacío en el payload
    CASE
        WHEN p.action_type IN ('ISOLATE_POD', 'QUARANTINE_NAMESPACE')
         AND (r.action_payload LIKE '%"podSelector": {}%'
              OR r.action_payload LIKE '%"podSelector":{}%')
        THEN 'WARN_EMPTY_POD_SELECTOR'
        ELSE 'OK'
    END AS pod_selector_status
FROM recommendation_ledger r
JOIN recommendation_policies p ON r.policy_id = p.policy_id
WHERE r.status = 'PENDING'
ORDER BY p.priority ASC, r.timestamp_utc ASC;

-- ── Políticas iniciales ───────────────────────────────────────────────────────

INSERT OR IGNORE INTO recommendation_policies VALUES (
    'POL_DNS_TUNNEL_001',
    'DNS Tunneling Detection — Isolate Pod',
    'REJECT',
    'T1071.004',
    'ISOLATE_POD',
    -- {resource_id} se reemplaza por el pod real antes del INSERT en recommendation_ledger
    '{"apiVersion":"networking.k8s.io/v1","kind":"NetworkPolicy","metadata":{"name":"vigia-isolate-{resource_id}"},"spec":{"podSelector":{"matchLabels":{"pod-name":"{resource_id}"}},"policyTypes":["Ingress","Egress"]}}',
    1,
    1,
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
);

INSERT OR IGNORE INTO recommendation_policies VALUES (
    'POL_PROCESS_INJECT_001',
    'Process Injection — Collect Forensics',
    'REJECT',
    'T1055',
    'COLLECT_FORENSICS',
    '{"action":"memory_dump","target_pod":"{resource_id}","tools":["volatility3","malfind"],"preserve_chain_of_custody":true}',
    1,
    1,
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
);

INSERT OR IGNORE INTO recommendation_policies VALUES (
    'POL_SA_TOKEN_THEFT_001',
    'Service Account Token Theft — Revoke SA Token',
    'REJECT',
    'T1528',
    'REVOKE_SA_TOKEN',
    '{"action":"revoke_token","service_account":"{resource_id}","namespace":"default","rotate_secret":true}',
    1,
    1,
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
);

INSERT OR IGNORE INTO recommendation_policies VALUES (
    'POL_ESCALATE_HUMAN_001',
    'Escalamiento humano — ABSTAIN con alta derivación',
    'ABSTAIN',
    NULL,
    'ESCALATE_HUMAN',
    '{"message":"VIGIA requires human review for resource {resource_id}. Verdict: ABSTAIN. Manual investigation required.","resource_id":"{resource_id}","escalation_level":"L2"}',
    2,
    1,
    strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
);

-- ── FIN DEL SCHEMA v3.1 ───────────────────────────────────────────────────────
-- Uso desde Python: ver recommendation_engine_v3.1.py
-- El ID de cada recommendation_ledger se calcula en Python como:
--   import hashlib, json
--   rec_id = hashlib.sha256(
--       f"{audit_id}|{policy_id}|{timestamp_utc}".encode()
--   ).hexdigest()
