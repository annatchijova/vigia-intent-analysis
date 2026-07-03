"""
vigia/core/vigia_scorer.py — DEPRECATED: re-export del scorer canónico.

B-055 FIX (Tanda B, 2026-07-03): este módulo era una copia divergente del
scorer vivo (`vigia_scorer.py`, raíz del repo) que referenciaba
`_EPC_FACTOR_TABLE` sin definirla — NameError latente en `_vigia_score` para
toda cadena de custodia no-BROKEN, en cuanto alguien la importara (ya estaba
flaggeada "stale and unused" por el patch r7, 2026-06-19).

Se congela como re-export para que NO pueda volver a divergir: una sola
fuente de verdad. Los consumidores reales (`vigia_api.py` ×2) ya importan la
raíz; este módulo existe solo por compatibilidad con imports externos.
"""
from __future__ import annotations

import sys as _sys

import vigia_scorer as _root

# Re-export completo (incluye nombres con guión bajo, que `import *` omite).
_sys.modules[__name__].__dict__.update({
    _k: _v for _k, _v in _root.__dict__.items()
    if not _k.startswith("__")
})
