"""Shim: BundleBuilder vive en ebs.py (evita ciclo con bundle_builder.py de raíz)."""
import importlib as _il, sys as _sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _root not in _sys.path: _sys.path.insert(0, _root)
_m = _il.import_module("ebs")
BundleBuilder = _m.BundleBuilder
