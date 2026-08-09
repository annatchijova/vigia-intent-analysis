"""
Purgatorio forense — sellado de modo POR DESCRIPTOR, no por nombre.

Origen: auditoría externa (DeepSeek), hallazgo TOCTOU. El mecanismo tal como
fue enunciado ("un atacante crea un symlink con el nombre del temporal en el
microsegundo entre que mkstemp() te da el nombre y tu código abre el FD") es
FALSO: `tempfile.mkstemp()` NO devuelve solo un nombre — devuelve `(fd, path)`,
creando y abriendo el archivo atómicamente con `O_CREAT|O_EXCL|O_NOFOLLOW`. No
existe ventana entre "obtener el nombre" y "abrir el FD" porque el FD viene del
mismo syscall. El `os.fstat(fd)` que la auditoría recomienda como defensa es,
por tanto, un no-op demostrable.

Lo que SÍ era un residuo real: `os.chmod(path, 0o400)` post-rename resuelve el
nombre y SIGUE symlinks, mientras que el chequeo `os.path.islink()` que lo
precede es un check-by-name. Un atacante local capaz de escribir en
`_PURGATORY_DIR` (uid propietario; el directorio es 0o700) podía sustituir el
temporal DESPUÉS del chequeo y hacer que el chmod aplicara 0o400 a un archivo
arbitrario. Cerrado sellando el modo con `os.fchmod()` sobre el descriptor.
"""

import os
import stat
import tempfile


class TestMkstempClosesTheStatedWindow:
    """La premisa del hallazgo enunciado es falsa — se fija en un test para
    que no vuelva a reabrirse como 'bug' en una auditoría futura."""

    def test_mkstemp_returns_an_open_fd_not_just_a_name(self):
        d = tempfile.mkdtemp()
        fd, path = tempfile.mkstemp(dir=d)
        try:
            assert isinstance(fd, int) and fd >= 0, (
                "mkstemp devuelve (fd, path): no hay ventana entre obtener el "
                "nombre y abrir el descriptor"
            )
            st = os.fstat(fd)
            assert stat.S_ISREG(st.st_mode), "mkstemp siempre crea archivo regular"
            # O_EXCL => el archivo no puede haber preexistido ni ser un symlink
            assert stat.S_IMODE(st.st_mode) == 0o600
        finally:
            os.close(fd)
            os.unlink(path)


class TestFchmodSealsTheInodeNotTheName:
    """El sellado 0o400 debe aplicarse al inodo escrito. Demostramos la
    diferencia observable entre fchmod (inodo) y chmod (nombre, sigue symlink)."""

    def test_fchmod_seals_the_written_inode(self):
        d = tempfile.mkdtemp()
        fd, path = tempfile.mkstemp(dir=d)
        try:
            os.write(fd, b"evidence")
            os.fchmod(fd, 0o400)
            assert stat.S_IMODE(os.lstat(path).st_mode) == 0o400
        finally:
            os.close(fd)

    def test_path_chmod_follows_symlink_but_fchmod_does_not(self):
        """Esta es la razón del cambio: chmod por ruta habría reescrito el
        modo del OBJETIVO del symlink; fchmod no puede."""
        d = tempfile.mkdtemp()
        victim = os.path.join(d, "victim")
        with open(victim, "wb") as fh:
            fh.write(b"unrelated file owned by the same uid")
        os.chmod(victim, 0o644)

        link = os.path.join(d, "swapped")
        os.symlink(victim, link)

        # chmod por ruta SIGUE el symlink — la víctima queda 0o400.
        os.chmod(link, 0o400)
        assert stat.S_IMODE(os.lstat(victim).st_mode) == 0o400, (
            "os.chmod sigue symlinks — este es exactamente el residuo cerrado"
        )
        # El symlink en sí no cambió de modo.
        assert stat.S_ISLNK(os.lstat(link).st_mode)


class TestQuarantineSourceUsesFdSealing:
    """Guarda de regresión sobre el código vivo: el sellado del Purgatorio no
    debe volver a hacerse con os.chmod() por ruta."""

    def _source(self):
        """Lee el cuerpo de la función desde el ARCHIVO, sin importar el
        módulo: `vigia_sift_bridge` arrastra dependencias opcionales (psutil)
        que no están garantizadas en un entorno mínimo, y esta guarda debe
        correr igual."""
        import ast
        from pathlib import Path

        path = Path(__file__).resolve().parents[1] / "vigia" / "vigia_sift_bridge.py"
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) \
                    and node.name == "_quarantine_malformed_evidence":
                return ast.get_source_segment(text, node) or ""
        raise AssertionError("_quarantine_malformed_evidence no encontrada")

    def test_uses_fchmod_on_descriptor(self):
        assert "os.fchmod(" in self._source(), (
            "el sellado 0o400 debe aplicarse por descriptor (fchmod)"
        )

    def test_does_not_chmod_the_renamed_final_path(self):
        src = self._source()
        assert "os.chmod(final_path" not in src, (
            "chmod por ruta post-rename reintroduce la ventana "
            "chmod-sigue-symlink que fchmod cierra"
        )

    def test_source_is_opened_with_o_nofollow(self):
        assert "O_NOFOLLOW" in self._source(), (
            "el archivo de evidencia origen nunca debe abrirse a través de un symlink"
        )
