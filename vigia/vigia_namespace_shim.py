# -*- coding: utf-8 -*-
"""
vigia_namespace_shim.py

SHIM DE NAMESPACE — VIGÍA repo flat → imports vigia.X

El repo VIGÍA es flat (todos los .py en el mismo directorio).
Los módulos usan imports de la forma `from vigia.core.X import Y`
que asumen una estructura de package con subdirectorios.

Este shim registra los módulos flat en sys.modules bajo sus nombres
completos del package, resolviendo imports circulares con placeholders.

USO: importar UNA VEZ antes de cualquier import vigia.X:
    import vigia_namespace_shim  # se auto-instala al importar

MANTENIMIENTO: Si se agrega un módulo con import vigia.X.nuevo,
agregar la línea en _ORDERED_IMPORTS al final del archivo.
"""
from __future__ import annotations

import sys
import types
import importlib
import os

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_INSTALLED = False


def _ensure_path() -> None:
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)


def _make_ns(name: str) -> types.ModuleType:
    """Namespace intermedio (vigia, vigia.core, etc.)."""
    if name in sys.modules and not getattr(sys.modules[name], '__vigia_ns__', False):
        return sys.modules[name]
    m = types.ModuleType(name)
    m.__path__ = [_REPO_ROOT]
    m.__package__ = name
    m.__vigia_ns__ = True
    sys.modules[name] = m
    return m


def _import_with_placeholder(vigia_path: str, flat_name: str) -> None:
    """
    Importa flat_name, resolviendo posibles imports circulares a vigia_path.
    1. Pre-registrar vigia_path como placeholder
    2. Importar flat_name (ve el placeholder si hace from vigia_path import X)
    3. Reemplazar placeholder con el módulo real
    """
    if vigia_path in sys.modules and not getattr(sys.modules[vigia_path], '__vigia_ns__', False) \
            and not getattr(sys.modules[vigia_path], '__vigia_placeholder__', False):
        return  # ya está el módulo real

    # Placeholder para romper circularidad
    if vigia_path not in sys.modules or getattr(sys.modules[vigia_path], '__vigia_ns__', False):
        ph = types.ModuleType(vigia_path)
        ph.__vigia_placeholder__ = True
        ph.__path__ = [_REPO_ROOT]
        sys.modules[vigia_path] = ph

    try:
        if flat_name not in sys.modules:
            importlib.import_module(flat_name)
        sys.modules[vigia_path] = sys.modules[flat_name]
    except ImportError:
        # Módulo flat no existe — dejar stub con advertencia
        stub = types.ModuleType(vigia_path)
        stub.__vigia_stub__ = True
        stub.__vigia_missing__ = flat_name
        sys.modules[vigia_path] = stub
    except Exception:
        # Importó con error parcial — usar lo que haya en sys.modules
        if flat_name in sys.modules:
            sys.modules[vigia_path] = sys.modules[flat_name]


# ── Orden de importación: base primero, dependientes después ─────────────────
# Formato: (vigia_path, flat_module_name)
# El orden importa: security antes que cualquier módulo que use vigia.security
_ORDERED_IMPORTS: list[tuple[str, str]] = [
    # Base — sin dependencias vigia.X internas
    ("vigia.security",         "security"),
    ("vigia.config",           "config"),
    ("vigia.sandbox",          "sandbox"),
    ("vigia.phonetic_loader",  "phonetic_loader"),
    # W4 (Claude 2026-05-02): visible_variables necesario para abductive_intent_engine.
    # Sin este alias, si el módulo se carga por namespace antes de que el path flat
    # esté disponible, el import `from visible_variables import` falla silenciosamente.
    ("vigia.visible_variables", "visible_variables"),
    ("vigia.inference.abductive_intent_engine", "abductive_intent_engine"),

    # Core
    ("vigia.core.signal_contract",     "signal_contract"),
    ("vigia.core.audit_action",        "audit_action"),
    ("vigia.core.likelihood_ratio",    "likelihood_ratio"),
    ("vigia.core.likelihood_engine",   "likelihood_engine"),
    ("vigia.core.graph_stability",     "graph_stability"),
    ("vigia.core.ebs_v1",              "ebs_v1"),
    ("vigia.core.bundle_builder",      "bundle_builder"),
    ("vigia.core.evidence_aggregator", "evidence_aggregator"),
    ("vigia.core.fit_calibration",     "fit_calibration"),
    ("vigia.core.pipeline",            "pipeline"),
    ("vigia.core.resource_optimizer",  "resource_optimizer"),
    ("vigia.core.risk_bounded_layer",  "risk_bounded_layer"),
    ("vigia.core.semiotic_detector_v2","semiotic_detector_v2"),

    # Forensics
    ("vigia.forensics.pki_tools", "pki_tools"),

    # Tools
    ("vigia.tools.nlp_constants",          "nlp_constants"),
    ("vigia.tools.forensic_db",            "forensic_db"),
    ("vigia.tools.mitre_mapping",          "mitre_mapping"),
    ("vigia.tools.adversarial_nlp",        "adversarial_nlp"),
    ("vigia.tools.document_integrity",     "document_integrity"),
    ("vigia.tools.vigia_sift_bridge",      "vigia_sift_bridge"),
    ("vigia.tools.vision_audit",           "vision_audit_final"),
    ("vigia.tools.vigia_adversarial_nlp",  "vigia_adversarial_nlp"),  # stub re-export
    ("vigia.tools.vigia_entanglement",     "vigia_entanglement"),     # stub re-export

    # Alias de seguridad
    ("vigia.security.sandbox", "sandbox"),
]


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _ensure_path()

    # Namespaces intermedios
    for ns in ("vigia", "vigia.core", "vigia.tools", "vigia.forensics", "vigia.security"):
        _make_ns(ns)
    sys.modules["vigia"].__vigia_shim__ = True

    # Importar en orden
    for vigia_path, flat_name in _ORDERED_IMPORTS:
        _import_with_placeholder(vigia_path, flat_name)

    _INSTALLED = True


install()
