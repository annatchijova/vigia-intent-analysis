"""
B6 — Enforcement de consistencia de los mapas de tipos (antecedente B-060).

B-060 (Lente 7/8) documentó el acoplamiento accidental: agregar un motor exige
tocar ≥2 namespaces de mapas (`artifact_type` → `_LAYER_MAP`/`_ONTOLOGY_MAP`;
`evidence_type` → `_EVIDENCE_MAP` → `EVIDENCE_PROFILES`/`_DOMAIN_MAP`) sin ningún
enforcement, y un tipo no cubierto degrada en silencio al peor default
(`DISK_MFT`, peso 4/10). La propuesta de B-060 ofrecía «un registro único O al
menos un test que falle si un `artifact_type` emitido por algún motor no está en
todos los mapas». Este archivo es ese test.

Diseño (docs/B6_ARTIFACT_TYPE_REGISTRY_DESIGN.md):
- Consistencia interna: `_LAYER_MAP` ≡ `_ONTOLOGY_MAP`; cierre de `_EVIDENCE_MAP`
  en `EVIDENCE_PROFILES` ∩ `_DOMAIN_MAP`.
- Cobertura de emisores: scan estático de los literales `"artifact_type"` /
  `"evidence_type"` que los motores asignan, cada uno debe estar mapeado o
  grandfathered con justificación.
- Honestidad del grandfather: cada entrada debe seguir emitida y sin mapear.

Límite conocido: el scan no detecta tipos computados dinámicamente. Ninguno de
los emisores actuales lo hace (misma limitación que test_requirements_ci_contract).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pytest

import vigia.core.forensic_adapter as FA
from vigia.tools import caie

REPO = Path(__file__).resolve().parent.parent

# Directorios de motores/adaptadores que emiten SignalOutput.
_SCAN_DIRS = ["vigia/sift", "vigia/tools", "vigia/inference", "vigia/core"]
_SCAN_ROOTS = ["sift_orchestrator.py"]

# Soporta la forma dict  "artifact_type": "x"  y la subscript  ["artifact_type"] = "x".
# El valor captura cualquier literal entre comillas ([^"']+), NO solo
# [a-z0-9_]: un tipo con mayúscula/guión/espacio no debe escapar del enforcement
# (era un false-negative del guard — CODE-REVIEW B6 #1).
_PAT_ART = re.compile(r'''["']artifact_type["']\s*\]?\s*[:=]\s*["']([^"']+)["']''')
_PAT_EV = re.compile(r'''["']evidence_type["']\s*\]?\s*[:=]\s*["']([^"']+)["']''')

# ── Grandfather: artifact_type emitidos que intencionalmente NO llevan capa
#    física, con la justificación de por qué su default es seguro. El test falla
#    si una entrada deja de emitirse (muerta) o pasa a estar mapeada (removerla).
_UNMAPPED_ARTIFACT_TYPES = {
    "behavioral": "meta-señal derivada (behavioral_fingerprint/metabolic), _mark_derived z=0; no es capa física",
    "resonance": "meta-señal derivada (cross_artifact_resonance), _mark_derived z=0",
    "pattern": "meta-señal derivada (case_pattern_library), _mark_derived z=0",
    "timeline": "meta-señal derivada (unified_timeline_engine), _mark_derived z=0",
    "pcap": "señal derivada del shim (resumen pcap), signal_class=derived inline z=0",
    "ioc": "IOCMatchResult.to_signal() no cableado en el pipeline determinista (enrich_signal es stub); latente",
}


def _scan_literals(pattern: re.Pattern) -> dict:
    """{valor -> [archivos]} para un patrón de literal emitido. Determinista.
    El árbol se lee una sola vez y se cachea (CODE-REVIEW B6 #2)."""
    out: dict = {}
    for f, txt in _source_files():
        for v in pattern.findall(txt):
            out.setdefault(v, []).append(f)
    return out


@lru_cache(maxsize=1)
def _source_files() -> tuple:
    """(ruta_relativa, contenido) de cada .py escaneado, leído una vez."""
    files = []
    for d in _SCAN_DIRS:
        files += sorted((REPO / d).rglob("*.py"))
    files += [REPO / r for r in _SCAN_ROOTS]
    out = []
    for f in files:
        try:
            out.append((f.relative_to(REPO).as_posix(), f.read_text(encoding="utf-8")))
        except OSError:
            continue
    return tuple(out)


def _emitted_artifact_types() -> dict:
    return _scan_literals(_PAT_ART)


def _emitted_evidence_types() -> dict:
    return _scan_literals(_PAT_EV)


# ── Consistencia interna de los mapas ───────────────────────────────────────

class TestMapInternalConsistency:
    def test_layer_and_ontology_have_identical_keys(self):
        """Los dos mapas del namespace `artifact_type` deben cubrir el mismo
        conjunto de claves: si uno tiene un tipo y el otro no, ese tipo recibe un
        default silencioso en una de las dos dimensiones."""
        layer = set(FA._LAYER_MAP)
        onto = set(FA._ONTOLOGY_MAP)
        assert layer == onto, (
            f"_LAYER_MAP y _ONTOLOGY_MAP divergen — "
            f"solo en LAYER: {sorted(layer - onto)}; "
            f"solo en ONTOLOGY: {sorted(onto - layer)}"
        )

    def test_evidence_map_output_closes_into_profiles_and_domains(self):
        """Todo `evidence_type` al que `_EVIDENCE_MAP` traduce debe existir como
        clave en `EVIDENCE_PROFILES` y en `_DOMAIN_MAP`; si no, el lookup de
        spoofability/dominio degrada al perfil default en silencio."""
        profiles = set(getattr(caie, "EVIDENCE_PROFILES", {}))
        domains = set(getattr(caie, "_DOMAIN_MAP", {}))
        outputs = set(FA._EVIDENCE_MAP.values())
        missing_prof = sorted(outputs - profiles)
        missing_dom = sorted(outputs - domains)
        assert not missing_prof, f"salidas de _EVIDENCE_MAP sin EVIDENCE_PROFILES: {missing_prof}"
        assert not missing_dom, f"salidas de _EVIDENCE_MAP sin _DOMAIN_MAP: {missing_dom}"


# ── Cobertura de emisores ───────────────────────────────────────────────────

class TestEmittedArtifactTypeCoverage:
    def test_every_emitted_artifact_type_is_mapped_or_grandfathered(self):
        emitted = _emitted_artifact_types()
        layer = set(FA._LAYER_MAP)
        offenders = {
            t: files for t, files in sorted(emitted.items())
            if t not in layer and t not in _UNMAPPED_ARTIFACT_TYPES
        }
        assert not offenders, (
            "artifact_type(s) emitidos por un motor pero ausentes de _LAYER_MAP "
            "y del grandfather (degradarían en silencio a DISK_MFT): "
            + "; ".join(f"{t} en {files}" for t, files in offenders.items())
            + " — mapealos en _LAYER_MAP/_ONTOLOGY_MAP o justificalos en "
            "_UNMAPPED_ARTIFACT_TYPES."
        )

    def test_windows_event_log_is_mapped_to_registry(self):
        """Regresión del gap activo B-096: la señal primaria del EventLogCorrelator
        usa artifact_type='windows_event_log', que debe pesar como REGISTRY (igual
        que 'event_log'), no caer al default DISK_MFT."""
        from vigia.core.forensic_adapter import EvidenceLayer
        assert FA._LAYER_MAP.get("windows_event_log") == EvidenceLayer.REGISTRY
        assert FA._LAYER_MAP["windows_event_log"] == FA._LAYER_MAP["event_log"]

    def test_abductive_record_gets_registry_layer_end_to_end(self):
        """Comportamiento real: signal_to_abductive_record sobre una señal con
        artifact_type='windows_event_log' produce un ArtifactRecord con capa
        REGISTRY (peso 6/10), no el default silencioso DISK_MFT (4/10)."""
        from vigia.core.forensic_adapter import SignalOutput, EvidenceLayer
        sig = SignalOutput(
            tool_name="EventLogCorrelator", value=0.9, z_score=3.4, confidence=0.8,
            metadata={"artifact_type": "windows_event_log", "signal_class": "primary"},
        )
        rec = FA.ForensicAdapter.signal_to_abductive_record(sig)
        assert rec.layer == EvidenceLayer.REGISTRY


class TestEmittedEvidenceTypeCoverage:
    def test_every_emitted_evidence_type_resolves(self):
        emitted = _emitted_evidence_types()
        profiles = set(getattr(caie, "EVIDENCE_PROFILES", {}))
        domains = set(getattr(caie, "_DOMAIN_MAP", {}))
        offenders = {}
        for t, files in sorted(emitted.items()):
            resolved = FA._EVIDENCE_MAP.get(t, t)
            miss = [name for name, S in (("EVIDENCE_PROFILES", profiles),
                                         ("_DOMAIN_MAP", domains)) if resolved not in S]
            if miss:
                offenders[t] = (resolved, miss, files)
        assert not offenders, (
            "evidence_type(s) emitidos que no resuelven en todos los mapas: "
            + "; ".join(f"{t}->{r} falta {m} ({f})" for t, (r, m, f) in offenders.items())
        )


# ── Honestidad del grandfather ──────────────────────────────────────────────

class TestGrandfatherHonesty:
    def test_no_dead_grandfather_entries(self):
        """Cada tipo grandfathered debe seguir siendo emitido por algún motor;
        si no, es una entrada muerta que oculta la lista real."""
        emitted = set(_emitted_artifact_types())
        dead = sorted(t for t in _UNMAPPED_ARTIFACT_TYPES if t not in emitted)
        assert not dead, (
            f"entradas grandfathered que ya nadie emite (removelas): {dead}"
        )

    def test_grandfather_entries_are_actually_unmapped(self):
        """Si un tipo grandfathered fue mapeado, hay que sacarlo del allowlist —
        de lo contrario el allowlist miente sobre el estado de los mapas."""
        layer = set(FA._LAYER_MAP)
        now_mapped = sorted(t for t in _UNMAPPED_ARTIFACT_TYPES if t in layer)
        assert not now_mapped, (
            f"tipos en el grandfather que ya están en _LAYER_MAP "
            f"(removelos del allowlist): {now_mapped}"
        )

    def test_every_grandfather_entry_has_a_reason(self):
        blank = sorted(t for t, r in _UNMAPPED_ARTIFACT_TYPES.items() if not str(r).strip())
        assert not blank, f"entradas grandfathered sin justificación: {blank}"
