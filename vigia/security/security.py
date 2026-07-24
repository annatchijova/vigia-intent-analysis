"""
vigia/security.py
=================
VIGÍA – Security subsystem.

Responsibilities
----------------
* SecurityAudit  : immutable append-only forensic log (the "black book").
* LLMShield      : prompt-injection & jailbreak firewall with Unicode NFKC
                   normalisation so homoglyph/leet bypasses are caught.
* _sanitize_path : path-traversal prevention (shared utility used by every
                   tool that touches the filesystem).
* TrustExponentialDecay : trust score degradation on provenance breaks

Design notes
------------
* SecurityAudit never swallows failures silently – it always emits to stderr
  AND raises a RuntimeError so the caller knows logging failed (forfeited
  forensic chain-of-custody is a critical event, not a soft warning).
* LLMShield normalises text to NFKC *before* pattern matching, then runs a
  second pass on the original text so that deliberate Unicode obfuscation is
  caught even if the canonical form looks clean.
* All public functions are synchronous so they can be called safely from both
  sync and async contexts without an extra event-loop wrapper.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import re
import secrets
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Final


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# B-135: the audit log must NEVER default into the evidence directory —
# evidence is read-only (Invariant 1). VIGIA_LOG_DIR is the same variable
# vigia/config.py already resolves for log_dir; the old fallback to
# VIGIA_EVIDENCE_DIR wrote security_audit.log into the forensic evidence
# tree on every default SecurityAudit() when that variable was set.
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")

# Maximum bytes stored per field to prevent log flooding
_MAX_PREVIEW_BYTES: Final[int] = 200

# P1-10: XML/HTML tag stripping for LLM input sanitization
_LLM_DANGEROUS_TAGS: Final[re.Pattern] = re.compile(
    r'</?(?:system|human|assistant|user|tool|result|instruction|inst|override)\b[^>]*>',
    re.IGNORECASE
)
_CONTROL_CHARS: Final[re.Pattern] = re.compile(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]')


def _create_secure_fallback_log() -> Path:
    """
    Create a secure fallback log file when the primary path is unavailable.

    Security measures (P0 fix — 2026-04 audit):
    * Uses tempfile.mkstemp() which creates the file atomically with
      O_EXCL — cannot be pre-created as a symlink by an attacker.
    * Sets permissions to 0o600 (owner read/write only).
    * Creates a dedicated directory with 0o700 if possible, to prevent
      other users from listing or accessing the file.
    * Verifies the created file is NOT a symlink (defense-in-depth).

    Previous version used a fixed path ("/tmp/vigia_security_audit.log")
    which was vulnerable to symlink attacks in multi-user systems.
    """
    import tempfile

    # Try to create a dedicated directory first
    fallback_dir = None
    try:
        fallback_dir = tempfile.mkdtemp(prefix="vigia_audit_")
        os.chmod(fallback_dir, 0o700)
    except OSError:
        fallback_dir = None  # Fall through to mkstemp in default tmpdir

    try:
        fd, path_str = tempfile.mkstemp(
            prefix="vigia_security_audit_",
            suffix=".log",
            dir=fallback_dir,
        )
        # mkstemp opens the file — close the fd, we'll reopen in append mode
        os.close(fd)
        # Restrict permissions: owner-only read/write
        os.chmod(path_str, 0o600)

        fallback_path = Path(path_str)

        # Defense-in-depth: verify it's not somehow a symlink
        if fallback_path.is_symlink():
            # This should be impossible with mkstemp, but paranoia is the policy
            os.unlink(path_str)
            raise OSError("mkstemp created a symlink — this should never happen")

        return fallback_path

    except OSError as exc:
        # Last resort: we literally cannot create a secure temp file.
        # Print to stderr and return a path that will fail on write,
        # which SecurityAudit handles by raising RuntimeError.
        print(
            f"[VIGIA][CRITICAL] Cannot create secure fallback log: {exc}. "
            "Audit logging will fail — forensic chain-of-custody is broken.",
            file=sys.stderr, flush=True,
        )
        return Path("/dev/null")  # writes succeed but are discarded

# HMAC key for log integrity chain.
# Priority: env var > file > auto-generated ephemeral key.
# In production, set VIGIA_HMAC_KEY or VIGIA_HMAC_KEY_FILE.
_HMAC_KEY_ENV: Final[str] = "VIGIA_HMAC_KEY"
_HMAC_KEY_FILE_ENV: Final[str] = "VIGIA_HMAC_KEY_FILE"
_HMAC_ALGORITHM: Final[str] = "sha256"

# Same fail-open-by-default / fail-closed-on-request pattern as
# VIGIA_ENFORCE_POSIX_SANDBOX (sandbox.py) and VIGIA_ENFORCE_STDIO /
# VIGIA_ENFORCE_PARENT / VIGIA_ENFORCE_KASSANDRA_SALT (vigia_sift_bridge.py).
# Without a persistent key, the entire security_audit.log HMAC chain resets
# on every process restart with a fresh, never-recorded key: a tampered or
# truncated log and a legitimate restart become indistinguishable, because
# there is nothing durable to verify the new chain against. Default is
# unchanged (warn + continue); set this to fail closed in production.
_ENFORCE_HMAC_KEY: Final[bool] = (
    os.getenv("VIGIA_ENFORCE_HMAC_KEY", "false").lower() == "true"
)


# ---------------------------------------------------------------------------
# TrustExponentialDecay
# ---------------------------------------------------------------------------

# P1-005 (Kimi 2026-05-02): math.exp usa FPU nativa — el bit 52 puede diferir
# entre x86/ARM o glibc/musl, invalidando determinismo Daubert en decisiones
# de custodia de evidencia. Fix: tabla de lookup con Decimal precomputado.
# Cubre el rango operativo λ·D ∈ [0.0, 6.0] en pasos de 0.25.
# Fuera del rango: clamp a los extremos (conservador).
#
# Valores: Decimal(str(round(math.exp(-x), 8))) para x en rango
# Generados offline con Python reference impl y fijados como constantes.
_EXP_DECAY_TABLE: dict[int, "Decimal"] = {}

def _build_exp_decay_table() -> None:
    """Construye la tabla de exp(-x) con Decimal una sola vez al importar."""
    import decimal as _dec
    ctx = _dec.Context(prec=28, rounding=_dec.ROUND_HALF_EVEN)
    # x = i * 0.25, i = 0..24 → cubre λD ∈ [0.0, 6.0]
    # Valores precomputados con referencia Python (deterministas)
    _precomputed = [
        "1.00000000", "0.77880078", "0.60653066", "0.47236655",
        "0.36787944", "0.28650480", "0.22313016", "0.17377394",
        "0.13533528", "0.10539922", "0.08208500", "0.06392786",
        "0.04978707", "0.03877421", "0.03019738", "0.02351775",
        "0.01831564", "0.01426423", "0.01110900", "0.00865169",
        "0.00673795", "0.00524752", "0.00408677", "0.00318278",
        "0.00247875",
    ]
    for i, val in enumerate(_precomputed):
        _EXP_DECAY_TABLE[i] = ctx.create_decimal(val)

_build_exp_decay_table()


def _exp_decay_decimal(x: "Decimal") -> "Decimal":
    """
    Calcula exp(-x) usando la tabla de lookup.
    Determinista cross-platform: sin FPU, solo Decimal.
    """
    from decimal import Decimal
    step = Decimal("0.25")
    # Índice = round(x / 0.25)
    idx = int((x / step).to_integral_value())
    idx = max(0, min(idx, len(_EXP_DECAY_TABLE) - 1))
    return _EXP_DECAY_TABLE[idx]


class TrustExponentialDecay:
    """
    Kimi P2: Trust score degradation on provenance chain breaks.

    When the Evidence Provenance Chain (EPC) detects a break, trust
    decays exponentially. If trust falls below threshold, adjusted
    scores are penalized.

    Formula: trust_effective = base_trust * exp(-lambda * break_severity)

    P1-005: exp() implementado con tabla Decimal para determinismo cross-platform.
    math.exp() con FPU puede diferir en bit 52 entre x86/ARM, invalidando Daubert.
    """

    def __init__(self, lambda_factor: float = 2.0, trust_threshold: float = 0.3):
        from decimal import Decimal
        self.lambda_factor = Decimal(str(lambda_factor))
        self.trust_threshold = Decimal(str(trust_threshold))

    def apply_decay(
        self,
        base_trust: float,
        break_severity: float = 1.0,
        adjusted_score: float = 0.0
    ) -> tuple[float, float]:
        """
        Apply exponential decay to trust and optionally penalize score.

        Returns:
            (trust_effective, score_after_penalty)
        """
        from decimal import Decimal
        zero = Decimal("0")
        one  = Decimal("1")

        bt = Decimal(str(base_trust))
        bs = Decimal(str(break_severity))

        exponent = self.lambda_factor * bs
        decay    = _exp_decay_decimal(exponent)

        trust_d = bt * decay
        trust_d = max(zero, min(one, trust_d))

        score_after_penalty = adjusted_score
        if trust_d < self.trust_threshold:
            score_after_penalty = adjusted_score * 0.5

        return trust_d, score_after_penalty


# Global instance for convenience
trust_decay = TrustExponentialDecay()


# ---------------------------------------------------------------------------
# SecurityAudit
# ---------------------------------------------------------------------------

class SecurityAudit:
    """
    Append-only forensic log with HMAC integrity chain.

    Every entry is a single JSON line containing an ``_hmac`` field that
    covers the entry content AND the HMAC of the previous entry. This
    creates a hash chain: tampering with any line invalidates all
    subsequent entries, making silent modification detectable.

    HMAC key resolution (priority order)
    -------------------------------------
    1. ``VIGIA_HMAC_KEY`` env var (hex-encoded, >= 32 bytes)
    2. ``VIGIA_HMAC_KEY_FILE`` env var pointing to a file with raw key bytes
    3. Auto-generated 32-byte ephemeral key (development/testing ONLY —
       key is lost on restart so the chain cannot be verified later)

    Verification
    ------------
    Call ``verify_chain()`` to walk the log and check every HMAC. Returns
    a list of line numbers where the chain breaks. Empty list = intact.

    Thread/async safety
    -------------------
    Each write opens, appends, and closes the file atomically enough for
    single-process use. For multi-process scenarios a proper log daemon
    (e.g. syslog / journald) should be the backend.
    """

    def __init__(self, log_path: str | None = None) -> None:
        candidate = Path(log_path) if log_path else Path(_DEFAULT_LOG_DIR) / "security_audit.log"
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            # Verify the candidate is not a pre-existing symlink (attack vector)
            if candidate.exists() and candidate.is_symlink():
                raise OSError(
                    f"Log path {candidate} is a symlink — refusing to write "
                    "(possible symlink attack)"
                )
            candidate.touch(exist_ok=True)
            # Restrict permissions on the log file
            try:
                os.chmod(str(candidate), 0o600)
            except OSError:
                pass  # best-effort — may fail on some filesystems
            self.log_path: Path = candidate
        except OSError as exc:
            fallback = _create_secure_fallback_log()
            msg = (
                f"[VIGIA][SecurityAudit] Cannot write to {candidate}: {exc}. "
                f"Falling back to secure temp: {fallback}"
            )
            print(msg, file=sys.stderr, flush=True)
            self.log_path = fallback

        # ── HMAC key resolution ───────────────────────────────────────────
        self._hmac_key: bytes = self._resolve_hmac_key()

        # ── Chain state: HMAC of the last written entry ───────────────────
        # On startup, recover the chain tail from the last line of the
        # existing log so we continue the chain rather than resetting it.
        self._prev_hmac: str = self._recover_chain_tail()

    # ------------------------------------------------------------------
    # HMAC key management
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_hmac_key() -> bytes:
        """
        Resolve the HMAC key from environment.

        Production: set VIGIA_HMAC_KEY (hex) or VIGIA_HMAC_KEY_FILE (path).
        Development: auto-generates an ephemeral key (logged as warning).
        """
        # 1. Direct env var (hex-encoded)
        key_hex = os.getenv(_HMAC_KEY_ENV, "").strip()
        if key_hex:
            try:
                key = bytes.fromhex(key_hex)
                if len(key) < 32:
                    print(
                        f"[VIGIA][SecurityAudit] WARNING: {_HMAC_KEY_ENV} is "
                        f"{len(key)} bytes — minimum 32 recommended.",
                        file=sys.stderr, flush=True,
                    )
                return key
            except ValueError:
                print(
                    f"[VIGIA][SecurityAudit] WARNING: {_HMAC_KEY_ENV} is not "
                    "valid hex. Falling through to next method.",
                    file=sys.stderr, flush=True,
                )

        # 2. Key file
        key_file = os.getenv(_HMAC_KEY_FILE_ENV, "").strip()
        if key_file:
            try:
                key_path = Path(key_file)
                if key_path.is_file():
                    key = key_path.read_bytes().strip()
                    if len(key) >= 32:
                        return key
                    print(
                        f"[VIGIA][SecurityAudit] WARNING: key file {key_file} "
                        f"contains only {len(key)} bytes.",
                        file=sys.stderr, flush=True,
                    )
            except OSError as exc:
                print(
                    f"[VIGIA][SecurityAudit] WARNING: cannot read key file "
                    f"{key_file}: {exc}",
                    file=sys.stderr, flush=True,
                )

        # 3. Ephemeral key (development only)
        msg = (
            f"No persistent HMAC key configured — set {_HMAC_KEY_ENV} or "
            f"{_HMAC_KEY_FILE_ENV} for production. Without one, the "
            "security_audit.log HMAC chain resets to a fresh, never-recorded "
            "key on every restart, so a tampered/truncated log cannot be "
            "told apart from a legitimate restart."
        )
        if _ENFORCE_HMAC_KEY:
            print(
                f"[VIGIA][SecurityAudit][CRITICAL] {msg} "
                "VIGIA_ENFORCE_HMAC_KEY=true — aborting.",
                file=sys.stderr, flush=True,
            )
            sys.exit(1)
        ephemeral = secrets.token_bytes(32)
        print(
            f"[VIGIA][SecurityAudit] WARNING: Using ephemeral HMAC key. {msg}",
            file=sys.stderr, flush=True,
        )
        return ephemeral

    def _recover_chain_tail(self) -> str:
        """
        Read the last line of the existing log and extract its _hmac
        so we can continue the chain seamlessly across restarts.

        Returns "GENESIS" if the log is empty or unreadable.
        """
        try:
            if not self.log_path.exists() or self.log_path.stat().st_size == 0:
                return "GENESIS"
            # Read last non-empty line efficiently
            with open(self.log_path, "rb") as fh:
                # Seek to end, walk backwards to find last newline
                fh.seek(0, 2)  # end
                pos = fh.tell()
                if pos == 0:
                    return "GENESIS"
                # Walk back up to 8KB to find the last complete line
                seek_back = min(pos, 8192)
                fh.seek(pos - seek_back)
                tail = fh.read().decode("utf-8", errors="replace")
            lines = [ln for ln in tail.strip().splitlines() if ln.strip()]
            if not lines:
                return "GENESIS"
            last_entry = json.loads(lines[-1])
            return last_entry.get("_hmac", "GENESIS")
        except (OSError, json.JSONDecodeError, KeyError):
            return "GENESIS"

    # ------------------------------------------------------------------
    # HMAC computation
    # ------------------------------------------------------------------

    def _compute_hmac(self, entry_json: str, prev_hmac: str) -> str:
        """
        Compute HMAC-SHA256 over (prev_hmac || entry_json).

        The prev_hmac links this entry to the previous one, creating an
        unbroken chain. Tampering with any entry invalidates all successors.
        """
        payload = f"{prev_hmac}||{entry_json}".encode("utf-8")
        return hmac.new(self._hmac_key, payload, _HMAC_ALGORITHM).hexdigest()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utcnow() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _truncate(text: str, max_bytes: int = _MAX_PREVIEW_BYTES) -> str:
        encoded = text.encode("utf-8", errors="replace")
        return encoded[:max_bytes].decode("utf-8", errors="replace")

    def _write_entry(self, entry: dict) -> None:
        """
        Write one JSON line with HMAC integrity chain and file locking.

        Concurrency safety (Kimi audit — 2026-04):
        Uses fcntl.flock(LOCK_EX) to serialize writes from multiple tools
        that may be running concurrently (e.g. parallel asyncio tasks in
        the investigation loop, or multiple VIGIA processes on the same
        log file). The lock is held for the minimum time: write + flush +
        fsync, then released.

        On non-POSIX systems (Windows), falls back to no locking with a
        warning on first call.

        Raises RuntimeError if the write fails.
        """
        # Inject chain link BEFORE serialization
        entry["_prev_hmac"] = self._prev_hmac

        # Serialize WITHOUT _hmac (it covers the serialized form)
        entry_json = json.dumps(entry, ensure_ascii=False, sort_keys=True)

        # Compute HMAC over the serialized entry + previous HMAC
        current_hmac = self._compute_hmac(entry_json, self._prev_hmac)
        entry["_hmac"] = current_hmac

        # Final serialized line (now includes _hmac)
        line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"

        try:
            with open(self.log_path, "a", encoding="utf-8") as fh:
                # Acquire exclusive file lock (blocks until available)
                try:
                    import fcntl
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                except (ImportError, OSError):
                    # Non-POSIX or lock not supported — proceed without lock
                    if not getattr(self, "_flock_warned", False):
                        print(
                            "[VIGIA][WARNING] fcntl.flock not available. "
                            "Audit log writes are not serialized. "
                            "Use single-process mode or deploy on POSIX.",
                            file=sys.stderr, flush=True,
                        )
                        self._flock_warned = True

                fh.write(line)
                fh.flush()
                os.fsync(fh.fileno())
                # Lock is released when fh is closed (end of with block)

        except OSError as exc:
            print(
                f"[VIGIA][CRITICAL] Audit log write failed: {exc}",
                file=sys.stderr,
                flush=True,
            )
            raise RuntimeError(
                f"VIGIA SecurityAudit: failed to persist log entry – "
                f"forensic chain-of-custody may be broken. Cause: {exc}"
            ) from exc

        # Advance chain state ONLY after successful write
        self._prev_hmac = current_hmac

    # ------------------------------------------------------------------
    # Chain verification
    # ------------------------------------------------------------------

    def verify_chain(self) -> list[dict]:
        """
        Walk the entire log and verify the HMAC chain.

        Returns a list of dicts describing each break found:
            [{"line": N, "expected_prev": "...", "found_prev": "...",
              "entry_timestamp": "..."}]

        Empty list means the chain is intact.

        NOTE: requires the same HMAC key that was used to write the log.
        If the key was ephemeral and the process restarted, verification
        will fail on the first entry after restart (expected behavior).
        """
        breaks: list[dict] = []
        prev_hmac = "GENESIS"
        chain_broken = False
        unverifiable_after = 0
        verified_count = 0

        try:
            with open(self.log_path, "r", encoding="utf-8") as fh:
                for line_num, raw_line in enumerate(fh, start=1):
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue

                    # If chain is already broken, mark remaining as unverifiable
                    if chain_broken:
                        unverifiable_after += 1
                        continue

                    try:
                        entry = json.loads(raw_line)
                    except json.JSONDecodeError:
                        breaks.append({
                            "line": line_num,
                            "error": "invalid JSON",
                            "raw_preview": raw_line[:100],
                        })
                        chain_broken = True
                        continue

                    stored_hmac = entry.pop("_hmac", "")
                    stored_prev = entry.get("_prev_hmac", "")

                    # Check chain link (constant-time comparison — P1 Kimi 2026-04)
                    if not hmac.compare_digest(
                        stored_prev.encode("utf-8"),
                        prev_hmac.encode("utf-8"),
                    ):
                        breaks.append({
                            "line": line_num,
                            "error": "prev_hmac mismatch (chain broken)",
                            "expected_prev": prev_hmac,
                            "found_prev": stored_prev,
                            "entry_timestamp": entry.get("timestamp", "?"),
                        })
                        chain_broken = True
                        continue

                    # Recompute HMAC to verify content integrity
                    entry_json = json.dumps(entry, ensure_ascii=False, sort_keys=True)
                    expected_hmac = self._compute_hmac(entry_json, stored_prev)

                    if not hmac.compare_digest(stored_hmac, expected_hmac):
                        breaks.append({
                            "line": line_num,
                            "error": "HMAC mismatch (content tampered)",
                            "entry_timestamp": entry.get("timestamp", "?"),
                        })
                        chain_broken = True
                        continue

                    prev_hmac = stored_hmac
                    verified_count += 1

        except OSError as exc:
            breaks.append({"line": 0, "error": f"cannot read log: {exc}"})

        if unverifiable_after > 0:
            breaks.append({
                "line": "N/A",
                "error": (
                    f"CHAIN_BROKEN: {unverifiable_after} entries after first break "
                    "were NOT verified (cannot trust HMACs after a break point). "
                    "All entries after the first tampered line are legally inadmissible."
                ),
                "unverifiable_entries": unverifiable_after,
                "verified_entries": verified_count,
            })

        return breaks

    # ------------------------------------------------------------------
    # WORM enforcement (Daubert / ISO 27037 compliance)
    # ------------------------------------------------------------------

    def enforce_worm(self) -> dict:
        """
        Attempt to set the immutable attribute on the audit log file
        using ``chattr +i`` (Linux ext4/xfs only, requires root/CAP_LINUX_IMMUTABLE).

        Once set, the file cannot be modified, deleted, or renamed by
        ANY user (including root) until ``chattr -i`` is called. This
        provides Write-Once-Read-Many (WORM) storage semantics required
        by ISO 27037 and Daubert admissibility standards.

        Returns a dict with:
            status    : "WORM_ACTIVE" | "WORM_FAILED" | "WORM_UNSUPPORTED"
            path      : the log file path
            error     : error message (only on failure)
            note      : operational guidance

        Prerequisites:
        * Linux with ext4, xfs, or btrfs filesystem
        * Root privileges or CAP_LINUX_IMMUTABLE capability
        * SIFT Workstation satisfies both requirements

        To undo (emergency only, breaks chain of custody):
            sudo chattr -i <log_path>
        """
        import platform
        import subprocess

        log_str = str(self.log_path)

        if platform.system() != "Linux":
            return {
                "status": "WORM_UNSUPPORTED",
                "path": log_str,
                "note": (
                    "WORM enforcement via chattr +i is Linux-only. "
                    "On other platforms, use a WORM-capable filesystem "
                    "(e.g. AWS S3 Object Lock, Azure Immutable Blob)."
                ),
            }

        try:
            result = subprocess.run(
                ["sudo", "chattr", "+i", log_str],
                capture_output=True,
                timeout=10,
                text=True,
            )
            if result.returncode == 0:
                self.log_info(
                    event_type="WORM_ENFORCED",
                    tool="SecurityAudit.enforce_worm",
                    message=f"chattr +i applied to {log_str}. File is now immutable.",
                )
                return {
                    "status": "WORM_ACTIVE",
                    "path": log_str,
                    "note": (
                        "Audit log is now immutable (chattr +i). "
                        "No process can modify or delete this file. "
                        "To unlock (breaks custody): sudo chattr -i " + log_str
                    ),
                }
            else:
                return {
                    "status": "WORM_FAILED",
                    "path": log_str,
                    "error": result.stderr.strip() or f"chattr returned {result.returncode}",
                    "note": (
                        "chattr +i failed. Common causes: "
                        "not running as root, filesystem does not support "
                        "immutable attribute (needs ext4/xfs/btrfs), or "
                        "sudo not configured for passwordless chattr."
                    ),
                }
        except FileNotFoundError:
            return {
                "status": "WORM_FAILED",
                "path": log_str,
                "error": "chattr command not found",
                "note": "Install e2fsprogs: sudo apt install e2fsprogs",
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "WORM_FAILED",
                "path": log_str,
                "error": "chattr timed out (sudo may require password)",
            }
        except Exception as exc:
            return {
                "status": "WORM_FAILED",
                "path": log_str,
                "error": str(exc),
            }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_block(
        self,
        event_type: str,
        tool: str,
        input_preview: str,
        reason: str,
        extra: dict | None = None,
    ) -> None:
        """
        Record a security-block event.

        Parameters
        ----------
        event_type   : e.g. "PROMPT_INJECTION", "PATH_TRAVERSAL"
        tool         : name of the VIGÍA tool that raised the alarm
        input_preview: raw input (will be truncated to 200 bytes)
        reason       : human-readable explanation
        extra        : optional dict with additional forensic metadata
        """
        entry: dict = {
            "timestamp": self._utcnow(),
            "level": "CRITICAL",
            "event_type": event_type,
            "tool_affected": tool,
            "input_preview": self._truncate(input_preview),
            "input_sha256": hashlib.sha256(
                input_preview.encode("utf-8", errors="replace")
            ).hexdigest(),
            "reason": reason,
            "process_id": os.getpid(),
        }
        if extra:
            entry["extra"] = extra

        self._write_entry(entry)

        # Immediate human-readable alert to the analyst's terminal
        print(
            f"\n[SECURITY ALERT] {entry['timestamp']} | {event_type} in '{tool}'\n"
            f"  REASON : {reason}\n"
            f"  INPUT  : {self._truncate(input_preview, 80)!r}\n",
            file=sys.stderr,
            flush=True,
        )

    def log_info(self, event_type: str, tool: str, message: str) -> None:
        """Record a non-blocking informational event (tool errors, retries…)."""
        entry: dict = {
            "timestamp": self._utcnow(),
            "level": "INFO",
            "event_type": event_type,
            "tool_affected": tool,
            "message": self._truncate(message, 500),
            "process_id": os.getpid(),
        }
        self._write_entry(entry)

    def log_tool_error(self, tool: str, kwargs_preview: str, error: str) -> None:
        """Convenience wrapper used by the Planner on tool failure."""
        self.log_info(
            event_type="TOOL_ERROR",
            tool=tool,
            message=f"kwargs={self._truncate(kwargs_preview)} | error={self._truncate(error, 300)}",
        )


# Module-level singleton – import and use anywhere without re-instantiation
audit_logger: SecurityAudit = SecurityAudit()


# ---------------------------------------------------------------------------
# LLMShield  (prompt-injection / jailbreak firewall)
# ---------------------------------------------------------------------------

# Base patterns (case-insensitive, applied after NFKC normalisation)
_INJECTION_PATTERNS_RAW: Final[list[str]] = [
    # Classic override instructions
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"disregard\s+(all\s+)?previous\s+instructions?",
    r"forget\s+(all\s+)?previous\s+instructions?",
    r"override\s+(all\s+)?previous\s+instructions?",
    r"you\s+are\s+now\s+(?:a\s+)?(?:different|new|another|evil|uncensored)",
    r"act\s+as\s+(?:if\s+you\s+(?:are|were)\s+)?(?:a\s+)?(?:different|new|another|evil|uncensored)",
    r"pretend\s+(?:you\s+are|to\s+be)\s+(?:a\s+)?(?:different|evil|unrestricted|uncensored)",
    # DAN / jailbreak families
    # P2 fix: \bDAN\b alone matches the name "Dan" in legal documents.
    # Require jailbreak context: "DAN mode", "you are DAN", "enable DAN", etc.
    r"(?:enable|activate|enter|switch\s+to|you\s+are)\s+DAN\b",
    r"\bDAN\s+(?:mode|jailbreak|prompt)",
    r"do\s+anything\s+now",
    r"jailbreak",
    r"unrestricted\s+mode",
    r"developer\s+mode",
    r"god\s+mode",
    # System prompt extraction
    r"reveal\s+(?:your\s+)?(?:system\s+prompt|instructions?|base\s+prompt)",
    r"print\s+(?:your\s+)?(?:system\s+prompt|instructions?)",
    r"show\s+(?:me\s+)?(?:your\s+)?(?:system\s+prompt|instructions?)",
    r"what\s+(?:are\s+)?(?:your\s+)?(?:initial\s+)?instructions?",
    # Role confusion
    r"you\s+(?:are|were)\s+(?:a|an)\s+(?:AI\s+)?(?:without|with\s+no)\s+(?:rules?|restrictions?|limits?)",
    r"(?:ignore|bypass|disable)\s+(?:your\s+)?(?:safety|ethical|content)\s+(?:filter|guidelines?|rules?)",
    # Token-stuffing delimiters sometimes used to inject
    r"<\s*/?(?:system|SYSTEM|SYS|instructions?)\s*>",
    r"\[\s*(?:SYSTEM|INST|OVERRIDE)\s*\]",
    # ── Domain-specific patterns (VIGÍA forensic context) ────────────────
    # An attacker who controls log content can inject these into evidence_summary.
    # Generic patterns above do NOT catch these — they use VIGIA's internal
    # vocabulary to manipulate the abductive reasoning verdict directly.
    # P3-H3: confirmed gap via red-team test 2026-05-02.
    r"system[_\-\s]*override\b",                           # SYSTEM_OVERRIDE: Set X
    r"set\s+intention[_\-\s]*symmetry",                    # set intention_symmetry to 1.0
    r"set\s+(?:confidence|trust|prior|posterior)\s+to\s+[01]",  # set confidence to 0
    r"ignore\s+(?:entropy|anomaly|anomalies|thirdness|peirce)",  # ignore entropy
    r"override\s+(?:verdict|thirdness|hypothesis|abduction)",    # override verdict
    r"(?:force|set)\s+(?:verdict|malice|intent)\s+to",          # force verdict to ACCEPT
    # P3-H3b: variantes específicas VIGÍA — red-team 2026-05-02 tanda 2
    r"vig[ií]a[_\-\s]*ignore",                                  # VIGÍA_IGNORE_THIS
    r"set\s+risk(?:[_\-\s]*score)?\s+to\s+\d",                  # set risk to 0 / set risk_score to 0
    r"ignore\s+(?:this\s+)?alert",                               # ignore this alert
    r"set\s+(?:intention|intent)\s+to\s+(?:benign|safe|clean)",  # set intention to benign
]

# Leet-speak transliteration table applied BEFORE pattern matching on the
# *original* (non-normalised) text to catch obfuscated variants.
_LEET_TABLE: Final[dict[str, str]] = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i",
}

_LEET_TRANS: Final = str.maketrans(_LEET_TABLE)


def _apply_leet(text: str) -> str:
    return text.translate(_LEET_TRANS)


def _nfkc(text: str) -> str:
    """Unicode NFKC normalisation – collapses homoglyphs to canonical form."""
    return unicodedata.normalize("NFKC", text)


def _compile_patterns(raw: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE | re.DOTALL) for p in raw]


_COMPILED_PATTERNS: Final[list[re.Pattern]] = _compile_patterns(_INJECTION_PATTERNS_RAW)


class LLMShield:
    """
    Firewall that sits in front of every LLM call and every user-supplied
    string that will be embedded in an LLM prompt.

    Scanning strategy (three passes)
    ---------------------------------
    1. NFKC-normalised text  → catches homoglyph substitution (е vs e, etc.)
    2. Leet-decoded text     → catches 1337 obfuscation
    3. Original text         → catches patterns that survive normalisation
    """

    def __init__(
        self,
        extra_patterns: list[str] | None = None,
        on_block: Callable[[str, str], None] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        extra_patterns : additional regex strings to add to the default set
        on_block       : optional callback(text, pattern) called on every block
                         (useful for testing / custom alerting)
        """
        patterns = list(_INJECTION_PATTERNS_RAW)
        if extra_patterns:
            patterns.extend(extra_patterns)
        self._patterns: list[re.Pattern] = _compile_patterns(patterns)
        self._on_block = on_block

    def scan(self, text: str, context: str = "unknown_tool") -> str:
        """
        Scan *text* for injection patterns.

        Returns the original text unchanged if clean.
        Raises ValueError and calls audit_logger if a pattern matches.
        """
        candidates = {
            "original": text,
            "nfkc": _nfkc(text),
            "leet": _apply_leet(text),
            "nfkc+leet": _apply_leet(_nfkc(text)),
        }

        for pass_name, candidate in candidates.items():
            for pattern in self._patterns:
                if pattern.search(candidate):
                    matched = pattern.pattern
                    reason = (
                        f"Injection pattern matched on {pass_name!r} pass: {matched!r}"
                    )
                    audit_logger.log_block(
                        event_type="PROMPT_INJECTION",
                        tool=context,
                        input_preview=text,
                        reason=reason,
                        extra={"pass": pass_name, "pattern": matched},
                    )
                    if self._on_block:
                        self._on_block(text, matched)
                    raise ValueError(
                        f"[LLMShield] Security block: potential prompt injection "
                        f"detected (pass={pass_name!r}). Input rejected."
                    )

        return text  # clean


# Module-level default shield instance
llm_shield: LLMShield = LLMShield()


# ---------------------------------------------------------------------------
# Free utility functions (module-level, importable directly)
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    """Return current UTC time as ISO-8601 string with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _truncate(text: str, max_bytes: int = _MAX_PREVIEW_BYTES) -> str:
    """
    Truncate *text* to at most *max_bytes* UTF-8 bytes, preserving valid
    Unicode at the boundary.  Safe to use on arbitrary untrusted input.
    """
    encoded = text.encode("utf-8", errors="replace")
    return encoded[:max_bytes].decode("utf-8", errors="replace")


# Alias so existing code using _sanitize_text keeps working
_sanitize_text = _truncate


# ---------------------------------------------------------------------------
# P1-10: Enhanced sanitization for LLM inputs
# ---------------------------------------------------------------------------

def _sanitize_llm_input(text: str, max_length: int = 5000) -> str:
    """
    Sanitize text before it enters an LLM prompt.

    P2-001 (Kimi 2026-05-02): unificada con la versión del planner.
    La versión anterior en security.py truncaba ciegamente (cleaned[:max_length]),
    lo que permite push-to-end attacks. Esta versión tiene NFKC + padding guard.

    0. NFKC normalization (MANDATORY FIRST): destruye homoglifos y caracteres
       Unicode invisibles usados para evasión de tokenizer.
    1. Strip XML/HTML tags que confunden al LLM (role-switching).
    2. Remove control characters (null, BEL, ESC, etc.).
    3. Padding anomaly guard: NO truncar ciegamente. Si el input supera
       max_length tras sanitización, rechazar y retornar sentinel forense.
    4. Log de todo lo que se eliminó.

    NOT a replacement for LLMShield (prompt injection patterns).
    """
    if not isinstance(text, str):
        return ""

    # STEP 0: NFKC — MUST BE FIRST
    text = unicodedata.normalize("NFKC", text)
    original_len = len(text)

    # STEP 1: Strip dangerous XML/role-switch tags
    cleaned = _LLM_DANGEROUS_TAGS.sub("[TAG_REMOVED]", text)

    # STEP 2: Strip control characters
    cleaned = _CONTROL_CHARS.sub("", cleaned)

    # STEP 3: Padding anomaly guard (no blind truncation)
    if len(cleaned) > max_length:
        audit_logger.log_block(
            event_type="EVIDENCE_PADDING_ANOMALY",
            tool="_sanitize_llm_input",
            input_preview=cleaned[:200],
            reason=(
                f"Input length {len(cleaned)} exceeds max_length={max_length} "
                "after NFKC+tag+control sanitization. "
                "Possible buffer-padding attack: injection payload may have been "
                "pushed to end of oversized input to survive blind truncation. "
                "Input REJECTED."
            ),
        )
        return (
            f"[EVIDENCE_PADDING_ANOMALY_DETECTED: "
            f"Input length {len(cleaned)} exceeds {max_length}. "
            "Possible buffer-hijack attempt. Original evidence rejected "
            "and flagged in forensic audit trail.]"
        )

    # STEP 4: Log si se eliminó contenido significativo
    if len(cleaned) < original_len - 10:
        audit_logger.log_info(
            event_type="LLM_INPUT_SANITIZED",
            tool="_sanitize_llm_input",
            message=(
                f"Stripped {original_len - len(cleaned)} chars from LLM input "
                "(homoglyphs/NFKC normalization, dangerous tags, or control chars)."
            ),
        )
    return cleaned


# ---------------------------------------------------------------------------
# _sanitize_path  (shared filesystem utility)
# ---------------------------------------------------------------------------

# Directories that are unconditionally blocked regardless of any other check.
_BLOCKED_PREFIXES: Final[tuple[str, ...]] = (
    "/etc",
    "/proc",
    "/sys",
    "/dev",
    "/boot",
    "/root",
    "/run",
    "/snap",
)


def _sanitize_path(
    raw: str,
    base_dir: str | None = None,
    must_exist: bool = False,
    allow_symlinks: bool = False,
) -> str:
    """
    Validate and canonicalise a file path.

    Rules (applied in order — first violation aborts)
    --------------------------------------------------
    1. Reject null bytes (C-string truncation attack).
    2. Reject empty / whitespace-only paths.
    3. Reject ``..`` components before resolution (fast fail).
    4. Resolve to absolute path.
    5. Symlink guard — checks EVERY component of the path, not just the
       leaf, to prevent intermediate-symlink escape (TOCTOU-resistant:
       uses ``os.lstat`` on the already-resolved path, not the raw input).
    6. Blocked system directory prefixes.
    7. Base-directory confinement.
    8. Existence check (optional).

    Returns the resolved absolute path as a string.
    Raises ValueError on any violation (also logs to audit_logger).

    Security notes (P0 fix — 2026-04 audit)
    ----------------------------------------
    * Previous version checked ``Path(raw).is_symlink()`` on the ORIGINAL
      path after ``resolve()`` had already followed symlinks — classic
      TOCTOU.  Now we check each component of the RESOLVED path via
      ``os.lstat()`` so there is no window between resolve and check.
    * Null byte rejection added: ``Path()`` handles them but downstream
      C code (subprocess, open()) truncates at \\x00.
    """

    # Track resolved path for canonical logging (set after step 4)
    _resolved_for_log: str = ""

    def _block(reason: str) -> None:
        extra = {"canonical_path": _resolved_for_log} if _resolved_for_log else None
        audit_logger.log_block(
            event_type="PATH_TRAVERSAL",
            tool="_sanitize_path",
            input_preview=raw,
            reason=reason,
            extra=extra,
        )
        raise ValueError(f"[VIGÍA] Path blocked: {reason} — input={raw!r}")

    # 1. Reject null bytes — MUST be first check
    #    A path like "/evidence/legit\x00/../../../etc/shadow" would pass
    #    Path().parts check but get truncated by C functions.
    if "\x00" in raw:
        _block("null byte in path (C-string truncation attack)")

    # 2. Reject null / empty
    if not raw or not raw.strip():
        _block("empty path")

    # 3. Reject raw ``..`` before resolution (fast fail)
    parts = Path(raw).parts
    if ".." in parts:
        _block("path traversal attempt (.. component)")

    # 4. Resolve to absolute path (follows symlinks to get canonical form)
    try:
        resolved = Path(raw).resolve()
    except (OSError, RuntimeError) as exc:
        # _block always raises, so 'resolved' is never used unbound.
        _block(f"path resolution error: {exc}")
        return ""  # unreachable — silences type checkers

    resolved_str = str(resolved)
    _resolved_for_log = resolved_str  # Enable canonical path in log entries

    # 5. Symlink guard — walk every component of the RESOLVED path
    #    This catches:
    #      a) The leaf itself being a symlink that points elsewhere
    #      b) Intermediate directories being symlinks (mount-escape)
    #    Uses os.lstat() + stat.S_ISLNK() — single atomic syscall,
    #    no race window between stat and check (Kimi P1 2026-04).
    if not allow_symlinks:
        import stat as _stat_mod

        # Check the full resolved path first (leaf node)
        try:
            st = os.lstat(resolved_str)
            if _stat_mod.S_ISLNK(st.st_mode):
                _block(
                    f"resolved path is a symlink: {resolved_str!r} "
                    f"(original input: {raw!r})"
                )
        except OSError as exc:
            _block(f"cannot lstat resolved path: {exc}")

        # Walk intermediate components from root to leaf
        accumulator = Path(resolved.anchor)
        for component in resolved.relative_to(resolved.anchor).parts:
            accumulator = accumulator / component
            try:
                st = os.lstat(str(accumulator))
                if _stat_mod.S_ISLNK(st.st_mode):
                    _block(
                        f"intermediate path component is a symlink: "
                        f"{str(accumulator)!r} (in resolved path {resolved_str!r})"
                    )
            except OSError:
                _block(
                    f"cannot stat intermediate component: "
                    f"{str(accumulator)!r}"
                )

    # 6. Blocked system prefixes
    for prefix in _BLOCKED_PREFIXES:
        if resolved_str == prefix or resolved_str.startswith(prefix + "/"):
            _block(f"path targets blocked system directory: {prefix!r}")

    # 7. Base-directory confinement
    if base_dir:
        # V-004 fix: validate base_dir itself before using it as trust anchor.
        # If base_dir is a symlink, an attacker who controls VIGIA_EVIDENCE_DIR
        # can redirect all path confinement to a different directory.
        base_path = Path(base_dir)
        if base_path.is_symlink():
            _block(
                f"base_dir is a symlink: {base_dir!r}. "
                "Evidence base directory cannot be a symlink — "
                "it is the trust anchor for path confinement."
            )
        if ".." in base_path.parts:
            _block(f"base_dir contains '..': {base_dir!r}")
        if "\x00" in base_dir:
            _block("base_dir contains null byte")

        try:
            base_resolved = str(Path(base_dir).resolve())
        except (OSError, RuntimeError) as exc:
            _block(f"base_dir resolution error: {exc}")
            return ""  # unreachable

        # Verify base_dir resolves to itself (no intermediate symlinks)
        if base_resolved != str(base_path.absolute()):
            # base_dir has intermediate symlinks — the resolved path differs
            # from the absolute path. This means some component in the chain
            # is a symlink, which could be exploited.
            if not allow_symlinks:
                _block(
                    f"base_dir resolves differently than expected: "
                    f"{base_dir!r} -> {base_resolved!r} (intermediate symlink?). "
                    "Set allow_symlinks=True to override."
                )

        if not resolved_str.startswith(base_resolved + "/") and resolved_str != base_resolved:
            _block(
                f"path escapes evidence base directory: "
                f"{resolved_str!r} not under {base_resolved!r}"
            )

    # 8. Existence check
    if must_exist and not resolved.exists():
        raise ValueError(f"[VIGÍA] Path does not exist: {resolved_str!r}")

    return resolved_str


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

import asyncio
import functools
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TypeVar, ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

_RATE_WINDOW_DEFAULT: Final[float] = 60.0
_RATE_CALLS_DEFAULT: Final[int] = 10
_BACKOFF_BASE: Final[float] = 2.0
_BACKOFF_MAX: Final[float] = 300.0
_BACKOFF_JITTER: Final[float] = 0.1


@dataclass
class _RateLimitEntry:
    calls: list = field(default_factory=list)
    consecutive_violations: int = 0
    backoff_until: float = 0.0


class _AdaptiveRateLimiter:
    """
    Sliding-window rate limiter with exponential backoff.

    One global instance is used for the whole process.  The asyncio.Lock
    makes it safe for concurrent coroutines on a single event loop.
    """

    def __init__(self) -> None:
        self._state: dict[str, _RateLimitEntry] = defaultdict(_RateLimitEntry)
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        # Create the lock lazily so the limiter can be imported at module level
        # before any event loop exists.
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    @staticmethod
    def _now() -> float:
        return time.monotonic()

    @staticmethod
    def _backoff(violations: int) -> float:
        raw = min(_BACKOFF_BASE ** violations, _BACKOFF_MAX)
        jitter = 1.0 + random.uniform(-_BACKOFF_JITTER, _BACKOFF_JITTER)
        return raw * jitter

    async def acquire(
        self,
        key: str,
        max_calls: int,
        window: float = _RATE_WINDOW_DEFAULT,
        caller: str = "",
    ) -> tuple[bool, dict]:
        """
        Return (allowed, metadata).

        allowed  : True if the call may proceed.
        metadata : diagnostic dict always present (retry_after, calls_remaining, …).
        """
        async with self._get_lock():
            now = self._now()
            entry = self._state[key]

            # Evict expired timestamps
            cutoff = now - window
            entry.calls = [t for t in entry.calls if t > cutoff]

            # Check active backoff
            if now < entry.backoff_until:
                retry_after = entry.backoff_until - now
                return False, {
                    "allowed": False,
                    "reason": "backoff_active",
                    "retry_after_seconds": round(retry_after, 2),
                    "consecutive_violations": entry.consecutive_violations,
                }

            # Check window limit
            if len(entry.calls) >= max_calls:
                entry.consecutive_violations += 1
                duration = self._backoff(entry.consecutive_violations)
                entry.backoff_until = now + duration
                audit_logger.log_info(
                    event_type="RATE_LIMIT_VIOLATION",
                    tool=caller or key,
                    message=(
                        f"{len(entry.calls)} calls in {window}s window. "
                        f"Backoff: {duration:.1f}s "
                        f"(violation #{entry.consecutive_violations})"
                    ),
                )
                return False, {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "retry_after_seconds": round(duration, 2),
                    "calls_in_window": len(entry.calls),
                    "max_calls": max_calls,
                    "consecutive_violations": entry.consecutive_violations,
                }

            # Allowed
            entry.calls.append(now)
            return True, {
                "allowed": True,
                "calls_remaining": max_calls - len(entry.calls),
                "window_seconds": window,
                "consecutive_violations": entry.consecutive_violations,
            }


_global_rate_limiter: _AdaptiveRateLimiter = _AdaptiveRateLimiter()


class RateLimitExceeded(Exception):
    """Raised when raise_on_limit=True and a rate limit is exceeded."""


def rate_limit(
    max_calls: int = _RATE_CALLS_DEFAULT,
    window_seconds: float = _RATE_WINDOW_DEFAULT,
    key_func: Callable[..., str] | None = None,
    raise_on_limit: bool = True,
) -> Callable:
    """
    Async decorator that enforces a sliding-window rate limit.

    Parameters
    ----------
    max_calls      : maximum calls allowed within *window_seconds*.
    window_seconds : rolling window duration in seconds.
    key_func       : callable(*args, **kwargs) -> str to derive the bucket
                     key.  Defaults to the decorated function's name.
    raise_on_limit : if True (default) raises RateLimitExceeded.
                     if False, returns a dict with status="RATE_LIMITED"
                     (better for MCP tools where the planner should decide).

    Usage
    -----
    @mcp.tool()
    @rate_limit(max_calls=5, window_seconds=60, raise_on_limit=False)
    async def reason_with_llm(evidence: str) -> dict:
        ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if key_func:
                try:
                    key = key_func(*args, **kwargs)
                except Exception as exc:
                    key = f"{func.__name__}:key_error"
                    audit_logger.log_info(
                        "RATE_LIMIT_KEY_ERROR", func.__name__, str(exc)
                    )
            else:
                key = func.__name__

            allowed, meta = await _global_rate_limiter.acquire(
                key=key,
                max_calls=max_calls,
                window=window_seconds,
                caller=func.__name__,
            )

            if not allowed:
                retry_after = meta.get("retry_after_seconds", window_seconds)
                audit_logger.log_block(
                    event_type="RATE_LIMIT_ENFORCED",
                    tool=func.__name__,
                    input_preview=f"key={key}",
                    reason=meta.get("reason", "rate_limit"),
                    extra=meta,
                )
                if raise_on_limit:
                    raise RateLimitExceeded(
                        f"Rate limit for '{key}': retry after {retry_after:.1f}s"
                    )
                return {  # type: ignore[return-value]
                    "status": "RATE_LIMITED",
                    "error": f"Rate limit exceeded. Retry after {retry_after:.1f}s.",
                    "retry_after_seconds": retry_after,
                    "timestamp": _utcnow(),
                }

            return await func(*args, **kwargs)

        wrapper._rate_limit_config = {  # type: ignore[attr-defined]
            "max_calls": max_calls,
            "window_seconds": window_seconds,
        }
        return wrapper

    return decorator


# P2 FIX: rate_limit_reset with atomic lock protection
async def rate_limit_reset(key: str) -> bool:
    """
    Clear rate-limit state for *key*.

    SECURITY: This function MUST NOT be exposed as an MCP tool.
    If an attacker can call rate_limit_reset("reason_with_llm"), they can
    bypass rate limits and perform denial-of-service against LLM backends.

    Intended for: testing, emergency manual resets via CLI/admin interface.
    Always logged to the forensic audit trail.

    P2 fix (2026-04 audit): Was synchronous but modified _state that is
    protected by asyncio.Lock in acquire(). Now acquires the lock to
    prevent data races with concurrent coroutines.
    """
    # Log at CRITICAL level — any reset is a security-relevant event
    audit_logger.log_block(
        event_type="RATE_LIMIT_RESET",
        tool="rate_limit_reset",
        input_preview=key,
        reason=f"Rate limit state cleared for key: {key!r}. Verify this was authorized.",
    )

    limiter = _global_rate_limiter
    async with limiter._get_lock():
        if key in limiter._state:
            del limiter._state[key]
            return True
    return False


async def rate_limit_status(key: str) -> dict:
    """Return current rate-limit state for *key* (for debugging/testing)."""
    limiter = _global_rate_limiter
    async with limiter._get_lock():
        entry = limiter._state.get(key, _RateLimitEntry())
        now = limiter._now()
        recent = [t for t in entry.calls if t > now - _RATE_WINDOW_DEFAULT]
        return {
            "key": key,
            "calls_in_window": len(recent),
            "consecutive_violations": entry.consecutive_violations,
            "backoff_active": now < entry.backoff_until,
            "backoff_until": entry.backoff_until if entry.backoff_until > now else None,
        }
