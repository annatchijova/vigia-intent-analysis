"""
vigia.core.atomic_io — escritura atómica de artefactos forenses (B-064).

Mismo patrón que el fix L-023 de `BundleBuilder.save` (bundle_builder.py):
mkstemp en el MISMO directorio + fsync + os.replace. Un crash o corte de
energía entre el write y el close nunca deja visible un artefacto a medio
escribir en el path destino — para ledgers, manifests, firmas, bundles y
reportes, un archivo truncado es una ruptura de cadena de custodia bajo
Daubert.
"""

import os
import tempfile


def _fsync_parent_dir(target_dir: str) -> None:
    """
    fsync del directorio contenedor tras os.replace (F-6, auditoría 2026-07-06).

    fsync del descriptor del archivo garantiza que los DATOS llegaron a disco,
    pero NO que la entrada de directorio (el rename de os.replace) sea durable.
    En algunos filesystems (ext4 con data=ordered por defecto) un crash
    inmediatamente posterior al rename puede perder la publicación y revertir
    al archivo previo — el artefacto de custodia sellado desaparece o retrocede:
    ruptura de cadena de custodia bajo Daubert. fsync del directorio lo cierra.

    Best-effort en plataformas sin fsync de directorio (p.ej. Windows, donde
    os.replace ya es atómico y la semántica de durabilidad difiere): se ignora
    silenciosamente sólo el caso no soportado, nunca un error de datos.
    """
    try:
        dir_fd = os.open(target_dir, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    except OSError:
        return  # el SO no permite abrir el directorio para fsync (no-POSIX)
    try:
        os.fsync(dir_fd)
    except OSError:
        # Algunos SO no soportan fsync sobre un fd de directorio.
        pass
    finally:
        os.close(dir_fd)


def _atomic_write(path: str, data, mode: str, encoding=None) -> None:
    abs_path = os.path.abspath(path)
    target_dir = os.path.dirname(abs_path) or "."
    os.makedirs(target_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=target_dir, prefix=".atomic_", suffix=".tmp")
    try:
        with os.fdopen(fd, mode, encoding=encoding) as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, abs_path)
    except BaseException:
        # No dejar tempfiles huérfanos si algo falla antes del replace.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    # Durabilidad del rename (F-6): sólo tras un os.replace exitoso. Si fallara
    # aquí, el artefacto YA está publicado en abs_path — por eso va fuera del
    # try/except que limpia tmp_path (que ya no existe).
    _fsync_parent_dir(target_dir)


def atomic_write_text(path: str, content: str, encoding: str = "utf-8") -> None:
    """Escribe texto de forma atómica (tempfile + fsync + os.replace)."""
    _atomic_write(path, content, "w", encoding=encoding)


def atomic_write_bytes(path: str, content: bytes) -> None:
    """Escribe bytes de forma atómica (tempfile + fsync + os.replace)."""
    _atomic_write(path, content, "wb")
