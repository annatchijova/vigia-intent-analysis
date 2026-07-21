"""
vigia/tools/forensic_db.py
===========================
VIGÍA — Gestor de base de datos SQLite forense.

Extraído de: adversarial_nlp_pericial_EN_ES.py (raíz)
Responsabilidad única: persistencia SQLite para perfiles ACP,
historial documental y audit trail Daubert.

SECURITY FEATURES
-----------------
- Path sanitization anti-traversal y anti-symlink (DeepSeek)
- File locking via fcntl (DeepSeek)
- WAL mode + límite de tamaño 500MB (Qwen Memory Paranoia)
- Anti-envenenamiento: rechaza actualizaciones si MCP > 2.5
- Trigger SQLite para mantener ventana deslizante de 20 docs/emisor
- Permisos de archivo: 0o640 (owner+group read, world none)

Importado por:
  - vigia/tools/adversarial_nlp.py  (ACP_Protocol, ForensicEngine)
  - vigia/tools/entanglement.py     (EntanglementEngine)

SANS FIND EVIL Hackathon 2026
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import sqlite3
import stat
import statistics
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from vigia.security import _utcnow, audit_logger
from vigia.tools.nlp_constants import (
    ACP_WINDOW_SIZE,
    DB_PERMISSIONS,
    CONFIG_PERMISSIONS,
    MAX_DB_SIZE,
    EVIDENCE_PATH_ENV,
)


class SecurityError(Exception):
    """Violación de seguridad en operaciones de persistencia forense."""
    pass


def validate_external_output_path(output_path: str, *, artifact_label: str) -> str:
    """Return a canonical output target that cannot mutate source evidence.

    A caller-provided output path carries write authority.  Derived artifacts
    must be validated before their parent directory exists, and every existing
    component is checked with ``lstat`` so an intermediate symlink cannot turn
    an apparently external target into an evidence write.
    """
    if not isinstance(output_path, str) or not output_path.strip():
        raise SecurityError("Output path must be a non-empty string")
    if "\x00" in output_path:
        raise SecurityError("Output path contains a null byte")

    raw_target = Path(os.path.abspath(os.path.expanduser(output_path)))
    current = Path(raw_target.anchor)
    for component in raw_target.parts[1:]:
        current /= component
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            # Descendants cannot exist until this component does.
            break
        except OSError as exc:
            raise SecurityError(
                f"Cannot inspect output path component: {current}"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise SecurityError(
                f"Output path contains symlink component: {current}"
            )

    try:
        target = raw_target.resolve(strict=False)
    except OSError as exc:
        raise SecurityError(f"Cannot resolve output path: {raw_target}") from exc

    evidence_dir = os.environ.get("VIGIA_EVIDENCE_DIR", "").strip()
    if evidence_dir:
        try:
            evidence_root = Path(
                os.path.abspath(os.path.expanduser(evidence_dir))
            ).resolve(strict=False)
        except OSError as exc:
            raise SecurityError(
                f"Cannot resolve VIGIA_EVIDENCE_DIR: {evidence_dir}"
            ) from exc
        if target == evidence_root or target.is_relative_to(evidence_root):
            raise SecurityError(
                f"Refusing to write {artifact_label} inside VIGIA_EVIDENCE_DIR "
                "(forensic evidence is read-only)"
            )

    return str(target)


class ForensicDatabaseManager:
    """
    Gestor Singleton de base de datos SQLite forense.

    DISEÑO SINGLETON: Una única instancia por proceso garantiza que
    todas las operaciones de escritura pasen por el mismo lock y evita
    aperturas concurrentes no coordinadas.

    ESQUEMA:
      - acp_profiles       : perfiles de autor con estadísticas rolling
      - document_history   : historial de documentos (ventana 20, via trigger)
      - audit_trail        : registro Daubert de todas las operaciones

    ANTI-ENVENENAMIENTO:
      No actualiza perfiles cuando MCP > 2.5 (posible spoofing activo).
    """

    _instance: Optional["ForensicDatabaseManager"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None) -> "ForensicDatabaseManager":
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return cls._instance

    def __init__(self, db_path: Optional[str] = None) -> None:
        if self._initialized:
            return

        if db_path is None:
            evidence_path = os.environ.get(EVIDENCE_PATH_ENV, "/mnt/evidence")
            db_path = os.path.join(evidence_path, "vigia_forensic.db")

        self.db_path: str = self._secure_path(db_path)
        self._ensure_directory()
        self._init_database()
        self._initialized = True

    # ------------------------------------------------------------------
    # Seguridad de path (DeepSeek)
    # ------------------------------------------------------------------

    def _secure_path(self, path: str) -> str:
        """Sanitización anti-traversal, anti-symlink, anti-world-writable."""
        abs_path = os.path.abspath(os.path.expanduser(path))

        if os.path.islink(abs_path):
            raise SecurityError(f"Database path cannot be symlink: {abs_path}")

        parent = os.path.dirname(abs_path)
        if not os.path.exists(parent):
            os.makedirs(parent, mode=0o750)

        try:
            stat_info = os.stat(parent)
            if stat_info.st_mode & 0o002:
                audit_logger.log_info(
                    event_type="DB_INSECURE_DIRECTORY",
                    tool="ForensicDatabaseManager",
                    message=f"Directory {parent} is world-writable — risk of tampering",
                )
        except OSError:
            pass

        return abs_path

    def _ensure_directory(self) -> None:
        parent = os.path.dirname(self.db_path)
        if not os.path.exists(parent):
            os.makedirs(parent, mode=0o750)

    # ------------------------------------------------------------------
    # Inicialización del esquema SQLite
    # ------------------------------------------------------------------

    def _init_database(self) -> None:
        """Crea esquema con WAL mode, índices y trigger de ventana deslizante."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA cache_size=-64000")  # 64 MB cache

            conn.execute("""
                CREATE TABLE IF NOT EXISTS acp_profiles (
                    emitter_id TEXT PRIMARY KEY,
                    emitter_type TEXT NOT NULL,
                    language TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    document_count INTEGER DEFAULT 0,
                    ttr_mean REAL DEFAULT 0.0,
                    ttr_std REAL DEFAULT 0.0,
                    ttr_history TEXT,
                    entropy_mean REAL DEFAULT 0.0,
                    entropy_std REAL DEFAULT 0.0,
                    entropy_history TEXT,
                    sync_mean REAL DEFAULT 0.0,
                    sync_std REAL DEFAULT 0.0,
                    sync_history TEXT,
                    last_verdict TEXT,
                    last_mcp REAL DEFAULT 0.0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emitter_id TEXT NOT NULL,
                    document_hash TEXT UNIQUE NOT NULL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ttr REAL,
                    entropy REAL,
                    sync_complexity REAL,
                    verdict TEXT,
                    mcp REAL,
                    FOREIGN KEY (emitter_id) REFERENCES acp_profiles(emitter_id)
                        ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    emitter_id TEXT,
                    document_hash TEXT,
                    details TEXT,
                    user_context TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_history_emitter
                ON document_history(emitter_id, analyzed_at DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp
                ON audit_trail(timestamp DESC)
            """)

            # Trigger: mantiene solo los últimos 20 documentos por emisor
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS limit_document_history
                AFTER INSERT ON document_history
                BEGIN
                    DELETE FROM document_history
                    WHERE emitter_id = NEW.emitter_id
                    AND id NOT IN (
                        SELECT id FROM document_history
                        WHERE emitter_id = NEW.emitter_id
                        ORDER BY analyzed_at DESC
                        LIMIT 20
                    );
                END
            """)

            conn.commit()
            os.chmod(self.db_path, DB_PERMISSIONS)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Context manager con file locking (DeepSeek)
    # ------------------------------------------------------------------

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Conexión con exclusive lock y verificación de tamaño."""
        lock_file = f"{self.db_path}.lock"
        with open(lock_file, "w") as lf:
            try:
                fcntl.flock(lf.fileno(), fcntl.LOCK_EX)

                size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                if size > MAX_DB_SIZE:
                    raise MemoryError(
                        f"Database exceeds size limit: {size} > {MAX_DB_SIZE}"
                    )

                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                try:
                    yield conn
                finally:
                    conn.close()
            finally:
                fcntl.flock(lf.fileno(), fcntl.LOCK_UN)

    # ------------------------------------------------------------------
    # CRUD de perfiles
    # ------------------------------------------------------------------

    def get_profile(self, emitter_id: str) -> Optional[Dict[str, Any]]:
        """Recupera perfil ACP con deserialización segura de historiales JSON."""
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM acp_profiles WHERE emitter_id = ?",
                (emitter_id,),
            ).fetchone()

            if row is None:
                return None

            result = dict(row)
            for key in ("ttr_history", "entropy_history", "sync_history"):
                raw = result.get(key)
                if raw:
                    try:
                        data = json.loads(raw)
                        # Limitar tamaño (Qwen)
                        result[key] = data[-ACP_WINDOW_SIZE:] if len(data) > ACP_WINDOW_SIZE else data
                    except (json.JSONDecodeError, TypeError):
                        result[key] = []
                else:
                    result[key] = []
            return result

    def update_profile(
        self,
        emitter_id: str,
        emitter_type: str,
        language: str,
        metrics: Dict[str, float],
        verdict: str,
        mcp: float,
        document_hash: str,
    ) -> bool:
        """
        Actualiza perfil ACP con protocolo anti-envenenamiento.

        Returns False si se rechazó (MCP > 2.5 indica spoofing activo).
        """
        if mcp > 2.5:
            self._log_audit(
                "PROFILE_UPDATE_REJECTED", emitter_id, document_hash,
                f"MCP={mcp:.2f} > 2.5 — possible active spoofing, update refused"
            )
            return False

        with self.connection() as conn:
            existing = conn.execute(
                "SELECT * FROM acp_profiles WHERE emitter_id = ?",
                (emitter_id,),
            ).fetchone()

            if existing:
                histories = self._update_histories(existing, metrics)
                stats = self._calculate_stats(histories)
                conn.execute("""
                    UPDATE acp_profiles SET
                        updated_at = CURRENT_TIMESTAMP,
                        document_count = document_count + 1,
                        ttr_mean = ?, ttr_std = ?, ttr_history = ?,
                        entropy_mean = ?, entropy_std = ?, entropy_history = ?,
                        sync_mean = ?, sync_std = ?, sync_history = ?,
                        last_verdict = ?, last_mcp = ?
                    WHERE emitter_id = ?
                """, (
                    stats["ttr"][0], stats["ttr"][1], json.dumps(histories["ttr"]),
                    stats["entropy"][0], stats["entropy"][1], json.dumps(histories["entropy"]),
                    stats["sync"][0], stats["sync"][1], json.dumps(histories["sync"]),
                    verdict, mcp, emitter_id,
                ))
            else:
                conn.execute("""
                    INSERT INTO acp_profiles (
                        emitter_id, emitter_type, language, document_count,
                        ttr_mean, ttr_std, ttr_history,
                        entropy_mean, entropy_std, entropy_history,
                        sync_mean, sync_std, sync_history,
                        last_verdict, last_mcp
                    ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    emitter_id, emitter_type, language,
                    metrics["ttr"], 0.0, json.dumps([metrics["ttr"]]),
                    metrics["entropy"], 0.0, json.dumps([metrics["entropy"]]),
                    metrics["sync"], 0.0, json.dumps([metrics["sync"]]),
                    verdict, mcp,
                ))

            conn.execute("""
                INSERT INTO document_history
                (emitter_id, document_hash, ttr, entropy, sync_complexity, verdict, mcp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                emitter_id, document_hash,
                metrics["ttr"], metrics["entropy"], metrics["sync"],
                verdict, mcp,
            ))
            conn.commit()

        self._log_audit("PROFILE_UPDATED", emitter_id, document_hash,
                        f"MCP={mcp:.2f} verdict={verdict}")
        return True

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _update_histories(
        self, existing: sqlite3.Row, new_metrics: Dict[str, float]
    ) -> Dict[str, list]:
        """Mantiene ventana deslizante de ACP_WINDOW_SIZE muestras."""
        histories: Dict[str, list] = {}
        for key in ("ttr", "entropy", "sync"):
            raw = existing[f"{key}_history"] or "[]"
            try:
                hist = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                hist = []
            hist.append(new_metrics.get(key, 0.0))
            histories[key] = hist[-ACP_WINDOW_SIZE:]
        return histories

    def _calculate_stats(
        self, histories: Dict[str, list]
    ) -> Dict[str, tuple[float, float]]:
        """Media y desvío estándar con protección contra división por cero."""
        stats: Dict[str, tuple[float, float]] = {}
        for key, values in histories.items():
            if len(values) >= 2:
                mean = statistics.mean(values)
                std = statistics.stdev(values) if len(set(values)) > 1 else 0.01
                stats[key] = (mean, max(std, 0.001))
            elif len(values) == 1:
                stats[key] = (values[0], 0.01)
            else:
                stats[key] = (0.0, 1.0)
        return stats

    def _log_audit(
        self, event_type: str, emitter_id: str, document_hash: str, details: str
    ) -> None:
        """Registro de auditoría Daubert en la tabla audit_trail."""
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO audit_trail
                (event_type, emitter_id, document_hash, details, user_context)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event_type, emitter_id, document_hash, details,
                os.environ.get("USER", "unknown"),
            ))
            conn.commit()

    # ------------------------------------------------------------------
    # Exportación para SIFT
    # ------------------------------------------------------------------

    def export_for_sift(self, export_path: str) -> str:
        """
        Exporta la DB completa para análisis externo en SIFT Workstation.
        Retorna el path del archivo exportado.
        """
        abs_export = validate_external_output_path(
            export_path, artifact_label="derived SQLite"
        )
        parent = os.path.dirname(abs_export)
        if not os.path.exists(parent):
            os.makedirs(parent, mode=0o750)

        # The directory creation above was intentionally delayed until after
        # the evidence-boundary check.  Re-check after it to catch a symlink
        # introduced by a concurrent local actor before SQLite opens the file.
        abs_export = validate_external_output_path(
            abs_export, artifact_label="derived SQLite"
        )

        with self.connection() as conn:
            backup_conn = sqlite3.connect(abs_export)
            try:
                conn.backup(backup_conn)
            finally:
                backup_conn.close()

        os.chmod(abs_export, CONFIG_PERMISSIONS)
        audit_logger.log_info(
            event_type="DB_EXPORTED_FOR_SIFT",
            tool="ForensicDatabaseManager",
            message=f"Database exported to {abs_export}",
        )
        return abs_export

    # ------------------------------------------------------------------
    # Utilidades de diagnóstico
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la DB para diagnóstico."""
        with self.connection() as conn:
            profile_count = conn.execute(
                "SELECT COUNT(*) FROM acp_profiles"
            ).fetchone()[0]
            doc_count = conn.execute(
                "SELECT COUNT(*) FROM document_history"
            ).fetchone()[0]
            audit_count = conn.execute(
                "SELECT COUNT(*) FROM audit_trail"
            ).fetchone()[0]

        size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        return {
            "db_path": self.db_path,
            "size_bytes": size,
            "profile_count": profile_count,
            "document_history_count": doc_count,
            "audit_trail_count": audit_count,
            "timestamp": _utcnow(),
        }

    @classmethod
    def reset_singleton(cls) -> None:
        """
        Resetea el singleton — SOLO para tests.
        No llamar en producción.
        """
        with cls._lock:
            cls._instance = None
