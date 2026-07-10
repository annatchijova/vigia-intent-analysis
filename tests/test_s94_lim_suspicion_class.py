"""
§9.4-LIM — clasificación de SUSPICION en el output del bundle (decisión sellada
2026-07-10, opción (ii) pura + extensión de narrativa aprobada).

Distingue dos clases que hoy son indistinguibles para el analista humano:
  GENERIC                  — poca evidencia / ambigüedad real.
  D3_RICH_NO_TRIANGULATION — anomalías fuertes (z>3, multi-vector) pero TODAS
                             confinadas al canal físico D3; por doctrina (ii)
                             no puede escalar sin segunda fuente (D2/D4/D5).

Regla exacta (diseño, docs/B052_P2_DESIGN.md §10):
  cond2 := ruta mobile-only (reasoner NOT_RUN_MOBILE_SINGLE_SOURCE)
           AND >=1 señal analizada (los marcadores unanalyzed no cuentan)
           AND TODAS las señales analizadas resuelven dominio D3
               (evidence_type|artifact_type -> _EVIDENCE_MAP -> _DOMAIN_MAP)
           AND max_z > 3        (umbral crítico pre-existente, Fraction)
           AND n_finding_types_distintos >= 2  (unión de metadata.finding_types)
  Dominio no resoluble o mapa no importable -> GENERIC (fail-closed).

INVARIANTE: solo narrativa + pipeline_meta. El veredicto sellado, el score y
el hypothesis NO cambian (gate comparativo 0 flips; pines abajo).
"""

from __future__ import annotations

import gzip
import io
import plistlib
import sqlite3
import struct
from fractions import Fraction
from pathlib import Path

import pytest

from vigia.sift.fsevents_parser import _SIG_V2, FLAG_REMOVED

NOTE_FRAGMENTS = (
    "confinada a un único canal físico (D3)",
    "segunda fuente independiente",
    "triangulación manual urgente",
)


# ── fixtures (mismos constructores que la sesión B-052-P2) ──────────────────

def _base(root: Path):
    (root / "SystemVersion.plist").write_bytes(
        plistlib.dumps({"ProductVersion": "13.0"}))


def _safari(root: Path, rows):
    safari = root / "Users" / "x" / "Library" / "Safari"
    safari.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(safari / "History.db"))
    c.execute("CREATE TABLE history_items(id INTEGER PRIMARY KEY, url TEXT, "
              "visit_count INTEGER)")
    c.execute("CREATE TABLE history_visits(id INTEGER PRIMARY KEY, "
              "history_item INTEGER, visit_time REAL, title TEXT)")
    for i, (u, t) in enumerate(rows, 1):
        c.execute("INSERT INTO history_items VALUES(?,?,?)", (i, u, 1))
        c.execute("INSERT INTO history_visits VALUES(?,?,?,?)", (i, i, 7e8 + i, t))
    c.commit()
    c.close()


def _fsevents_mass_delete(root: Path, n=30):
    fs = root / ".fseventsd"
    fs.mkdir(exist_ok=True)
    recs = b"".join(
        (f"Users/x/d{i}".encode() + b"\x00" + struct.pack("<Q", i)
         + struct.pack("<I", FLAG_REMOVED) + struct.pack("<Q", i))
        for i in range(n))
    pg = struct.pack("<4sII", _SIG_V2, 0, 12 + len(recs)) + recs
    b = io.BytesIO()
    with gzip.GzipFile(fileobj=b, mode="wb", mtime=0) as f:
        f.write(pg)
    (fs / "0000000000000001").write_bytes(b.getvalue())


def _launchagent(root: Path):
    la = root / "Users" / "x" / "Library" / "LaunchAgents"
    la.mkdir(parents=True, exist_ok=True)
    (la / "com.evil.plist").write_bytes(plistlib.dumps({
        "Label": "com.evil", "ProgramArguments": ["/tmp/evil"],
        "RunAtLoad": True, "KeepAlive": True}))


def _rich_d3(tmp_path) -> Path:
    """z=3.8 (exploit+antiforensic), 3 finding_types, todo D3 → cond2."""
    _base(tmp_path)
    _safari(tmp_path, [("https://exploit-db.com/CVE-1", "metasploit")])
    _fsevents_mass_delete(tmp_path)
    _launchagent(tmp_path)
    return tmp_path


def _single_vpn(tmp_path) -> Path:
    """z=1.6, 1 finding_type → GENERIC (ambigüedad real, no límite D3)."""
    _base(tmp_path)
    _safari(tmp_path, [("https://x/best-vpn-service", "vpn")])
    return tmp_path


def _weak_multi(tmp_path) -> Path:
    """z=1.2 piso, multi-tipo → GENERIC (multi-vector pero débil)."""
    _base(tmp_path)
    fs = tmp_path / ".fseventsd"
    fs.mkdir()
    rec = (b"Users/x/.Trash/f\x00" + struct.pack("<Q", 1)
           + struct.pack("<I", FLAG_REMOVED) + struct.pack("<Q", 1))
    pg = struct.pack("<4sII", _SIG_V2, 0, 12 + len(rec)) + rec
    b = io.BytesIO()
    with gzip.GzipFile(fileobj=b, mode="wb", mtime=0) as f:
        f.write(pg)
    (fs / "0000000000000001").write_bytes(b.getvalue())
    _launchagent(tmp_path)
    return tmp_path


def _analyze(evidence_dir):
    import sift_orchestrator as shim
    return shim.SIFTOrchestrator(case_id="S94LIM").analyze(
        macos_evidence_path=str(evidence_dir))


# ── condición 2: D3-rico sin triangulación ──────────────────────────────────

class TestD3RichNoTriangulation:
    def test_marker_set_in_pipeline_meta(self, tmp_path):
        r = _analyze(_rich_d3(tmp_path))
        assert r.get("pipeline_meta", {}).get("suspicion_class") \
            == "D3_RICH_NO_TRIANGULATION"

    def test_narrative_carries_the_doctrine_note(self, tmp_path):
        r = _analyze(_rich_d3(tmp_path))
        narr = r.get("abduction", {}).get("narrative", "")
        for frag in NOTE_FRAGMENTS:
            assert frag in narr, f"falta en narrativa: {frag!r}"
        assert "§9.4-LIM" in narr

    def test_verdict_and_score_unchanged(self, tmp_path):
        """INVARIANTE: la extensión es narrativa pura. Pin del comportamiento
        sellado MEDIDO pre-extensión (2026-07-10, esta rama): hypothesis
        INTENT_DETECTED, max_z 19/5, is_conclusive True, verdict INTENT.
        (La discrepancia INTENT vs techo SUSPICION de doctrina (ii) está
        documentada en §9.4-LIM — su enforcement requiere firma aparte;
        este cambio NO la corrige ni la empeora.)"""
        from vigia_agent import classify_agent_verdict, _signal_stats
        r = _analyze(_rich_d3(tmp_path))
        ab = r.get("abduction", {})
        assert ab.get("best_hypothesis") == "INTENT_DETECTED"
        assert r.get("pipeline_meta", {}).get("max_mobile_z") == "19/5"
        assert ab.get("is_conclusive") is True
        n_p, n_u = _signal_stats(r)
        assert classify_agent_verdict(ab, n_p, n_u) == "INTENT"


# ── SUSPICION genérico: sin el texto adicional ──────────────────────────────

class TestGenericStaysGeneric:
    @pytest.mark.parametrize("builder", [_single_vpn, _weak_multi])
    def test_marker_generic_and_no_note(self, tmp_path, builder):
        r = _analyze(builder(tmp_path))
        pm = r.get("pipeline_meta", {})
        assert pm.get("suspicion_class") == "GENERIC"
        narr = r.get("abduction", {}).get("narrative", "")
        for frag in NOTE_FRAGMENTS:
            assert frag not in narr, (
                f"el SUSPICION genérico no debe llevar la nota §9.4-LIM: {frag!r}")


# ── unidad: regla exacta y fail-closed ──────────────────────────────────────

class TestSuspicionClassRule:
    def _sig(self, z, ftypes, artifact_type="macos_forensic", **meta_extra):
        return {"tool": "MacOSForensics", "z_score": z,
                "metadata": {"artifact_type": artifact_type,
                             "finding_types": ftypes, **meta_extra}}

    def _cls(self, signals):
        import sift_orchestrator as shim
        zs = []
        for s in signals:
            try:
                zs.append(abs(Fraction(str(s.get("z_score", 0)))))
            except (ValueError, ZeroDivisionError):
                zs.append(Fraction(0))
        max_z = max(zs) if zs else Fraction(0)
        return shim._mobile_suspicion_class(signals, max_z)

    def test_all_conditions_met(self):
        assert self._cls([self._sig(3.8, ["A", "B", "C"])]) \
            == "D3_RICH_NO_TRIANGULATION"

    def test_z_at_threshold_is_generic(self):
        # umbral estricto: z==3 NO dispara (>3, mismo criterio que el gate
        # crítico del reasoner y _mobile_hypothesis)
        assert self._cls([self._sig(3.0, ["A", "B"])]) == "GENERIC"

    def test_single_finding_type_is_generic(self):
        assert self._cls([self._sig(3.8, ["A"])]) == "GENERIC"

    def test_non_d3_signal_fails_closed(self):
        # una señal de memoria (D2) rompe el confinamiento → hay triangulación
        # potencial → GENERIC
        sigs = [self._sig(3.8, ["A", "B"]),
                {"tool": "vol3", "z_score": 3.5,
                 "metadata": {"evidence_type": "memory_process",
                              "finding_types": ["C"]}}]
        assert self._cls(sigs) == "GENERIC"

    def test_unknown_domain_fails_closed(self):
        # artifact_type no resoluble a dominio → GENERIC (fail-closed)
        assert self._cls([self._sig(3.8, ["A", "B"],
                                    artifact_type="mystery_engine")]) == "GENERIC"

    def test_unanalyzed_markers_do_not_count(self):
        # solo marcadores unanalyzed → sin señales analizadas → GENERIC
        sigs = [{"tool": "x", "z_score": 0,
                 "metadata": {"unanalyzed": True, "artifact_type": "macos_forensic",
                              "finding_types": []}}]
        assert self._cls(sigs) == "GENERIC"

    def test_types_union_across_signals(self):
        # 2 señales D3 con 1 tipo cada una, distintos → unión >=2 → dispara
        sigs = [self._sig(3.8, ["A"]),
                self._sig(2.0, ["B"], artifact_type="ios_forensic")]
        assert self._cls(sigs) == "D3_RICH_NO_TRIANGULATION"
