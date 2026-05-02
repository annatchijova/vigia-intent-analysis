"""
vigia/__init__.py — Shim de compatibilidad de paquete.

Los módulos del proyecto residen en la raíz del repositorio.
Este paquete reexporta desde ahí para satisfacer imports del tipo
`from vigia.core.X import Y` sin mover archivos ni duplicar código.

Generado automáticamente — no editar manualmente.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
