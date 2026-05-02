"""Shim: reexporta vision_audit desde raíz del proyecto."""
import importlib as _il, sys as _sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _root not in _sys.path: _sys.path.insert(0, _root)
_m = _il.import_module("vision_audit")
globals().update({k: getattr(_m, k) for k in dir(_m) if not k.startswith("__")})
