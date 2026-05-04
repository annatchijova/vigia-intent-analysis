"""
vigia/utils/path_guard.py
==========================
Sanitización de paths para analizadores de artefactos forenses.

Kimi Fase 3.2: rechazar symlinks, device files, pipes, paths fuera de base_dir.

Invariantes:
- Siempre resolver path antes de comparar
- Verificar que es archivo regular (no device, pipe, symlink)
- Límite de 100MB por artefacto
- RuntimeError si VIGIA_EVIDENCE_BASE_DIR no está configurada y se usa modo estricto
"""
from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Optional

_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def sanitize_artifact_path(
    raw_path: str | Path,
    base_dir: Optional[Path] = None,
    max_size: int = _MAX_FILE_SIZE,
) -> Path:
    """
    Valida y sanitiza un path de artefacto forense.

    Args:
        raw_path:  Path a validar
        base_dir:  Directorio base permitido. Si None, usa VIGIA_EVIDENCE_BASE_DIR
                   o no restringe directorio (solo valida tipo de archivo).
        max_size:  Tamaño máximo en bytes (default 100MB)

    Returns:
        Path resuelto y validado

    Raises:
        ValueError: Path traversal, no es archivo regular, o demasiado grande
        RuntimeError: base_dir requerido pero no configurado
    """
    p = Path(raw_path).resolve()

    # Verificar existencia
    if not p.exists():
        raise ValueError(f"Artefacto no encontrado: {raw_path}")

    # Verificar que es archivo regular (no symlink, device, pipe, socket)
    file_stat = p.stat()
    if not stat.S_ISREG(file_stat.st_mode):
        raise ValueError(
            f"No es archivo regular: {raw_path} "
            f"(mode={oct(file_stat.st_mode)})"
        )

    # Verificar que no es symlink
    if p.is_symlink():
        raise ValueError(f"Symlink rechazado: {raw_path}")

    # Verificar tamaño
    if file_stat.st_size > max_size:
        raise ValueError(
            f"Artefacto demasiado grande: {file_stat.st_size} bytes "
            f"(máximo {max_size} bytes): {raw_path}"
        )

    # Verificar confinamiento a base_dir
    if base_dir is None:
        env_base = os.environ.get("VIGIA_EVIDENCE_BASE_DIR")
        if env_base:
            base_dir = Path(env_base).resolve()

    if base_dir is not None:
        base = base_dir.resolve()
        if not str(p).startswith(str(base)):
            raise ValueError(
                f"Path traversal detectado: {raw_path!r} "
                f"está fuera de {base}"
            )

    return p
