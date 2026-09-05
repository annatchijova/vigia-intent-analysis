"""MITRE ATT&CK lookups for the audience reports.

Descriptions come from ``vigia.tools.mitre_mapping.MASTER_TTP_DICTIONARY`` and
are MITRE's own English text: external vocabulary, rendered verbatim in both
languages. Ids that are not in VIGÍA's local dictionary get a URL derived from
the id pattern and are labeled as such; the report never invents a name.

``vigia.tools.mitre_mapping`` imports ``vigia.security`` (audit logger, which
announces itself on stderr). The import is therefore lazy and guarded: if it
fails, every lookup reports ``dictionary_available=False`` and the renderer
says so, rather than silently claiming the id is unknown (honest degradation,
docs/ENGINEERING_DISCIPLINE.md section 5.3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

_MITRE_BASE = "https://attack.mitre.org/techniques/"


@dataclass(frozen=True)
class TTPDescription:
    technique_id: str
    name: Optional[str]          # None when not in the local dictionary
    description: Optional[str]
    url: str
    in_local_dictionary: bool
    dictionary_available: bool   # False only when the dictionary failed to import


def mitre_url(technique_id: str) -> str:
    """Canonical ATT&CK URL for ``T1234`` or ``T1234.001``."""
    return _MITRE_BASE + technique_id.replace(".", "/")


def _lookup() -> Optional[Callable[[str], Any]]:
    try:
        from vigia.tools.mitre_mapping import get_ttp_metadata
    except Exception:  # noqa: BLE001 — degrade visibly, see module docstring
        return None
    return get_ttp_metadata


def describe_ttp(technique_id: str) -> TTPDescription:
    lookup = _lookup()
    if lookup is None:
        return TTPDescription(
            technique_id=technique_id, name=None, description=None,
            url=mitre_url(technique_id), in_local_dictionary=False,
            dictionary_available=False,
        )
    meta = lookup(technique_id)
    if meta is None:
        return TTPDescription(
            technique_id=technique_id, name=None, description=None,
            url=mitre_url(technique_id), in_local_dictionary=False,
            dictionary_available=True,
        )
    return TTPDescription(
        technique_id=technique_id, name=meta.name, description=meta.description,
        url=meta.url or mitre_url(technique_id), in_local_dictionary=True,
        dictionary_available=True,
    )


__all__ = ["TTPDescription", "describe_ttp", "mitre_url"]
