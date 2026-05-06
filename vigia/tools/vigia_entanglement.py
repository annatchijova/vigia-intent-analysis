# -*- coding: utf-8 -*-
"""
vigia/tools/vigia_entanglement.py — COMPATIBILITY STUB

Este módulo re-exporta desde entanglement.py del repo flat.
Existe para resolver el import lazy en temporal_forensics_redteam.py:
    from vigia.tools.vigia_entanglement import EntanglementEngine

El código real está en entanglement.py.
NO modificar este archivo directamente — modificar el original.
"""
from entanglement import EntanglementEngine

__all__ = ["EntanglementEngine"]
