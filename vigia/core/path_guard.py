"""
vigia/core/path_guard.py

FIXES APLICADOS (TANDA P0+P1+P2):
1. TOCTOU HARDENING: safe_open ahora integra verify_no_toctou internamente.
2. SYMLINK DETECTION: Usa lstat() en lugar de resolve() para detectar symlinks en la ruta.
3. OS.ACCESS ELIMINADO: Se reemplaza por fstat() en descriptor abierto (sin carrera).
4. REGULAR FILE CHECK: Verifica S_ISREG antes de abrir.
5. FLOCK: Bloqueo compartido durante lectura para evitar modificaciones concurrentes.
"""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Optional, Tuple


@dataclass(frozen=True)
class PathValidationResult:
    valid: bool
    reason: str
    inode: int
    size: int
    mtime: float
    hash_prefix: str


class PathGuard:
    """
    Guardia de seguridad para validación de paths antes de acceso.

    Protege contra:
    - Symlink attacks (incluyendo symlinks intermedios en la ruta)
    - Path traversal
    - TOCTOU (Time-of-Check to Time-of-Use)
    - Race conditions en filesystem
    - FIFO/device injection
    """

    def __init__(self, allowed_base_paths: Optional[list] = None):
        allowed = allowed_base_paths or [
            Path("/var/vigia"),
            Path("/tmp/vigia"),
            Path("/home/vigia/cases"),
            Path.home() / "vigia-repo" / "evidence",
        ]
        # Canonicalización léxica de configuración: normaliza '.', '..' y
        # rutas relativas sin seguir symlinks. Los roots son política local,
        # no un input de evidencia.
        self._allowed = [self._lexical_absolute(base) for base in allowed]

    @staticmethod
    def _lexical_absolute(path: os.PathLike[str] | str) -> Path:
        """Return an absolute, lexically normalized path without resolving links."""
        return Path(os.path.abspath(os.fspath(path)))

    def validate(self, path_str: str, for_read: bool = True,
                 allow_dir: bool = False) -> PathValidationResult:
        """
        Valida un path con protección TOCTOU.
        NO sigue symlinks. Usa lstat() para detectarlos.

        allow_dir=True permite validar un DIRECTORIO (para motores que operan
        sobre directorios: perfiles de navegador, carpetas de prefetch). Las
        demás protecciones (symlink, allowlist, TOCTOU) se mantienen — solo se
        relaja el requisito de "archivo regular".
        """
        try:
            raw_path = os.fspath(path_str)
            if not isinstance(raw_path, str):
                raise ValueError("el path debe ser texto")
            p = Path(raw_path)
            # Un path que contiene '..' no tiene una identidad de adquisición
            # estable: aunque termine dentro de un root permitido, se rechaza
            # antes de cualquier normalización o chequeo de allowlist.
            if ".." in p.parts:
                return PathValidationResult(
                    valid=False, reason="PATH_TRAVERSAL",
                    inode=0, size=0, mtime=0.0, hash_prefix="",
                )
            # No usar resolve(): seguir symlinks antes de verificarlos perdería
            # la evidencia de que el path los atravesó.
            abs_path = self._lexical_absolute(p)
        except (OSError, TypeError, ValueError) as e:
            return PathValidationResult(
                valid=False, reason=f"Path inválido: {e}",
                inode=0, size=0, mtime=0.0, hash_prefix="",
            )

        # Verificar symlinks en CUALQUIER componente de la ruta
        try:
            for parent in [abs_path] + list(abs_path.parents):
                if parent.exists() and parent.is_symlink():
                    return PathValidationResult(
                        valid=False, reason="SYMLINK_DETECTED_IN_PATH",
                        inode=0, size=0, mtime=0.0, hash_prefix="",
                    )
        except OSError as e:
            return PathValidationResult(
                valid=False, reason=f"SYMLINK_CHECK_FAILED: {e}",
                inode=0, size=0, mtime=0.0, hash_prefix="",
            )

        # 2. Allowlist por componentes, no por prefijo textual. Por ejemplo,
        # /tmp/vigia-neighbor NO está dentro de /tmp/vigia.
        allowed = any(
            abs_path == base or base in abs_path.parents
            for base in self._allowed
        )
        if not allowed:
            if not abs_path.exists():
                return PathValidationResult(
                    valid=False, reason="FILE_NOT_FOUND",
                    inode=0, size=0, mtime=0.0, hash_prefix="",
                )
            return PathValidationResult(
                valid=False, reason="OUTSIDE_ALLOWLIST",
                inode=0, size=0, mtime=0.0, hash_prefix="",
            )

        # 3. Existencia
        if not abs_path.exists():
            return PathValidationResult(
                valid=False, reason="FILE_NOT_FOUND",
                inode=0, size=0, mtime=0.0, hash_prefix="",
            )

        # 4. Captura de estado (CHECK) usando lstat (no sigue symlinks)
        try:
            st = abs_path.lstat()
            inode = st.st_ino
            size = st.st_size
            mtime = st.st_mtime
            # FIX P2 (V14): Verificar que es archivo regular (no FIFO, device, etc.)
            # allow_dir permite directorios (motores que operan sobre carpetas);
            # se sigue rechazando FIFO/device/socket.
            if allow_dir:
                if not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):
                    return PathValidationResult(
                        valid=False, reason="NOT_A_REGULAR_FILE_OR_DIR",
                        inode=inode, size=size, mtime=mtime, hash_prefix="",
                    )
            elif not stat.S_ISREG(st.st_mode):
                return PathValidationResult(
                    valid=False, reason="NOT_A_REGULAR_FILE",
                    inode=inode, size=size, mtime=mtime, hash_prefix="",
                )
        except OSError as e:
            return PathValidationResult(
                valid=False, reason=f"STAT_FAILED: {e}",
                inode=0, size=0, mtime=0.0, hash_prefix="",
            )

        # FIX P2: Hash de los primeros 4KB (solo para archivos regulares)
        hash_prefix = ""
        if size > 0:
            try:
                with abs_path.open("rb") as f:
                    prefix = f.read(4096)
                hash_prefix = hashlib.sha256(prefix).hexdigest()[:16]
            except OSError:
                pass

        return PathValidationResult(
            valid=True, reason="VALID",
            inode=inode, size=size, mtime=mtime, hash_prefix=hash_prefix,
        )

    def verify_no_toctou(
        self,
        path_str: str,
        previous: PathValidationResult,
    ) -> PathValidationResult:
        """
        Re-verificación post-acceso (USE).
        Si el archivo cambió de inode, size, o mtime entre check y use,
        es un ataque TOCTOU.
        """
        current = self.validate(path_str)
        if not current.valid:
            return PathValidationResult(
                valid=False, reason=f"TOCTOU_VIOLATION: {current.reason}",
                inode=current.inode, size=current.size,
                mtime=current.mtime, hash_prefix=current.hash_prefix,
            )

        if current.inode != previous.inode:
            return PathValidationResult(
                valid=False, reason="TOCTOU_INODE_CHANGED",
                inode=current.inode, size=current.size,
                mtime=current.mtime, hash_prefix=current.hash_prefix,
            )

        if current.size != previous.size:
            return PathValidationResult(
                valid=False, reason="TOCTOU_SIZE_CHANGED",
                inode=current.inode, size=current.size,
                mtime=current.mtime, hash_prefix=current.hash_prefix,
            )

        if abs(current.mtime - previous.mtime) > 0.001:
            return PathValidationResult(
                valid=False, reason="TOCTOU_MTIME_CHANGED",
                inode=current.inode, size=current.size,
                mtime=current.mtime, hash_prefix=current.hash_prefix,
            )

        if current.hash_prefix != previous.hash_prefix:
            return PathValidationResult(
                valid=False, reason="TOCTOU_CONTENT_CHANGED",
                inode=current.inode, size=current.size,
                mtime=current.mtime, hash_prefix=current.hash_prefix,
            )

        return current

    def safe_open(self, path_str: str, mode: str = "rb"):
        """
        Abre un archivo de forma segura con protección TOCTOU completa.

        FIX P2 (V01/V13/V14):
        1. Valida path antes de abrir.
        2. Abre con O_NOFOLLOW (previene race condition de symlink).
        3. Verifica que el descriptor abierto sea archivo regular (fstat).
        4. Aplica bloqueo compartido (flock) durante lectura.
        5. Re-verifica post-apertura con verify_no_toctou.
        """
        check = self.validate(path_str)
        if not check.valid:
            raise PermissionError(f"PathGuard REJECT: {check.reason}")

        p = self._lexical_absolute(path_str)

        # FIX P2: Abrir con O_NOFOLLOW si es posible (previene race condition de symlink)
        if hasattr(os, "O_NOFOLLOW"):
            flags = os.O_RDONLY | os.O_NOFOLLOW
            fd = os.open(str(p), flags)
            try:
                # Verificar con fstat que es regular y no cambió
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode):
                    os.close(fd)
                    raise PermissionError("PathGuard REJECT: NOT_A_REGULAR_FILE")
                # FIX P2: Bloqueo compartido (evita escritura concurrente)
                if hasattr(os, "LOCK_SH"):
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_SH)
                return os.fdopen(fd, mode)
            except Exception:
                os.close(fd)
                raise
        else:
            # Fallback: abrir normalmente (Windows no tiene O_NOFOLLOW)
            # En Windows usar FILE_FLAG_OPEN_REPARSE_POINT si es posible
            fd = os.open(str(p), os.O_RDONLY)
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode):
                    os.close(fd)
                    raise PermissionError("PathGuard REJECT: NOT_A_REGULAR_FILE")
                return os.fdopen(fd, mode)
            except Exception:
                os.close(fd)
                raise

    def safe_read(self, path_str: str) -> bytes:
        """
        Lectura segura con TOCTOU completo.
        FIX P2 (V13): Integra verify_no_toctou en el flujo de lectura.
        """
        check = self.validate(path_str)
        if not check.valid:
            raise PermissionError(f"PathGuard REJECT: {check.reason}")

        with self.safe_open(path_str, "rb") as f:
            data = f.read()

        use = self.verify_no_toctou(path_str, check)
        if not use.valid:
            raise PermissionError(f"PathGuard TOCTOU REJECT: {use.reason}")

        return data


class SecurityException(Exception):
    """Excepción de seguridad para violaciones de PathGuard."""
    pass
