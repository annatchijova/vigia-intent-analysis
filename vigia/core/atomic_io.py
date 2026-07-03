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


def atomic_write_text(path: str, content: str, encoding: str = "utf-8") -> None:
    """Escribe texto de forma atómica (tempfile + fsync + os.replace)."""
    _atomic_write(path, content, "w", encoding=encoding)


def atomic_write_bytes(path: str, content: bytes) -> None:
    """Escribe bytes de forma atómica (tempfile + fsync + os.replace)."""
    _atomic_write(path, content, "wb")
