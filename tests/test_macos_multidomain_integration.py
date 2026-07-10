"""
Test de integración multi-dominio del engine macOS.

Objetivo (precondición B-052-P2, docs/B052_P2_DESIGN.md §8.3): demostrar, con
un fixture sintético rico, que los parsers implementados esta sesión (Safari
history + Safari plists satélite + FSEvents + Spotlight + persistencia plist)
COMPONEN evidencia con MÚLTIPLES corr_groups distintos.

Esto es la mitad "necesaria" de B-052-P2 hecha concreta: hoy `to_signal()`
colapsa todo en UNA señal (medido: tuck-2019 = 1 corr_group → 1 señal → ABSTAIN),
pero un caso RICO ya produce ≥3 dominios de recolección — así que cuando
B-052-P2 (firmado) convierta `to_signal()` en `to_signals()` por dominio, ESTE
fixture es su prueba de aceptación: ≥3 señales primarias → el reasoner corre.

Cero código de producto: solo mide y pinea la composición de dominios.
"""

from __future__ import annotations

import gzip
import io
import plistlib
import sqlite3
import struct
from collections import Counter
from pathlib import Path

import pytest

from vigia.sift.macos_forensics import MacOSForensicsAnalyzer
from vigia.sift.fsevents_parser import _SIG_V2, FLAG_REMOVED

# Core Data epoch (segundos desde 2001-01-01) para visit_time de Safari.
_COREDATA_OFFSET = 978307200


def _write_safari_history(safari: Path):
    """History.db con el esquema que _analyze_safari espera + una URL de
    exploit (browser_suspicious)."""
    db = safari / "History.db"
    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE history_items (id INTEGER PRIMARY KEY, url TEXT, "
                 "visit_count INTEGER)")
    conn.execute("CREATE TABLE history_visits (id INTEGER PRIMARY KEY, "
                 "history_item INTEGER, visit_time REAL, title TEXT)")
    rows = [
        ("https://www.apple.com/", "Apple"),
        ("https://exploit-db.com/exploits/CVE-2024-0001", "metasploit payload"),
        ("https://forum.example/how-to-hack-wifi", "how to hack"),
    ]
    vt = 700000000  # Core Data seconds (dentro de rango plausible)
    for i, (url, title) in enumerate(rows, start=1):
        conn.execute("INSERT INTO history_items VALUES (?,?,?)", (i, url, 1))
        conn.execute("INSERT INTO history_visits VALUES (?,?,?,?)",
                     (i, i, vt + i, title))
    conn.commit()
    conn.close()


def _write_bookmarks(safari: Path):
    """Bookmarks.plist con un exploit bookmarkeado (browser_suspicious)."""
    tree = {"WebBookmarkType": "WebBookmarkTypeList", "Children": [
        {"WebBookmarkType": "WebBookmarkTypeLeaf",
         "URLString": "https://www.apple.com/", "URIDictionary": {"title": "Apple"}},
        {"WebBookmarkType": "WebBookmarkTypeLeaf",
         "URLString": "https://exploit-db.com/CVE-2024-0002",
         "URIDictionary": {"title": "metasploit"}},
    ]}
    (safari / "Bookmarks.plist").write_bytes(plistlib.dumps(tree))


def _write_fseventsd(root: Path):
    """.fseventsd con 30 eventos Removed (antiforensic: mass deletion)."""
    fs = root / ".fseventsd"
    fs.mkdir()
    recs = b"".join(
        (f"Users/x/doc{i}.txt".encode() + b"\x00"
         + struct.pack("<Q", i) + struct.pack("<I", FLAG_REMOVED)
         + struct.pack("<Q", 1000 + i))
        for i in range(30))
    page = struct.pack("<4sII", _SIG_V2, 0, 12 + len(recs)) + recs
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as f:
        f.write(page)
    (fs / "0000000000000001").write_bytes(buf.getvalue())


def _write_spotlight(root: Path):
    """Spotlight Shortcuts con consulta anti-forense (antiforensic)."""
    prefs = root / "Users" / "x" / "Library" / "Preferences"
    prefs.mkdir(parents=True, exist_ok=True)
    (prefs / "com.apple.spotlight.Shortcuts").write_bytes(
        plistlib.dumps({"bleachbit": {"DISPLAY_NAME": "cleaner"},
                        "weather": {}}))


def _write_persistence(root: Path):
    """LaunchAgent con ejecutable en /tmp (persistence)."""
    la = root / "Users" / "x" / "Library" / "LaunchAgents"
    la.mkdir(parents=True, exist_ok=True)
    (la / "com.evil.agent.plist").write_bytes(plistlib.dumps({
        "Label": "com.evil.agent",
        "ProgramArguments": ["/tmp/evil_payload"],
        "RunAtLoad": True, "KeepAlive": True,
    }))


@pytest.fixture
def rich_macos(tmp_path):
    (tmp_path / "SystemVersion.plist").write_bytes(
        plistlib.dumps({"ProductVersion": "13.0"}))
    safari = tmp_path / "Users" / "x" / "Library" / "Safari"
    safari.mkdir(parents=True)
    _write_safari_history(safari)
    _write_bookmarks(safari)
    _write_fseventsd(tmp_path)
    _write_spotlight(tmp_path)
    _write_persistence(tmp_path)
    return tmp_path


class TestMultiDomainComposition:
    def test_rich_evidence_produces_at_least_three_domains(self, rich_macos):
        r = MacOSForensicsAnalyzer().analyze(rich_macos)
        groups = Counter(f.corr_group for f in r.findings)
        distinct = set(groups)
        # La precondición B-052-P2: ≥3 dominios de recolección distintos.
        assert len(distinct) >= 3, (
            f"solo {len(distinct)} dominio(s): {dict(groups)} — el caso rico "
            f"no compone multi-dominio"
        )
        # Los dominios esperados de los 5 parsers:
        assert "browser_suspicious" in distinct   # history + bookmark
        assert "antiforensic" in distinct         # fsevents mass-deletion + spotlight
        assert "persistence" in distinct          # launchagent /tmp

    def test_each_parser_contributes(self, rich_macos):
        r = MacOSForensicsAnalyzer().analyze(rich_macos)
        fts = {f.finding_type for f in r.findings}
        # Safari history + bookmark → SAFARI_EXPLOIT_RESEARCH/SAFARI_SUSPICIOUS
        assert any(f.startswith("SAFARI_") for f in fts), fts
        # FSEvents → mass deletion
        assert "ANTIFORENSIC_FSEVENTS_MASS_DELETION" in fts
        # Spotlight → anti-forensic query
        assert "ANTIFORENSIC_SPOTLIGHT_QUERY" in fts
        # Persistence → suspicious launch agent
        assert "PERSISTENCE_SUSPICIOUS_LAUNCHAGENT" in fts

    def test_aggregate_signal_still_single_today(self, rich_macos):
        # Documenta el estado ACTUAL (pre-B-052-P2): pese a ≥3 dominios,
        # to_signal() colapsa todo en UNA señal. Es exactamente lo que
        # B-052-P2 desbloquea. Este assert es el "antes" del cambio.
        r = MacOSForensicsAnalyzer().analyze(rich_macos)
        sig = r.to_signal()
        # una sola señal agregada, un solo artifact_type
        assert sig.metadata["artifact_type"] == "macos_forensic"
        # el z agregado escala (tiene antiforensic + persistencia): documenta
        # el valor actual para la decisión de recalibración D1.
        assert sig.z_score > 0
        # nº de corr_groups que B-052-P2 fanearía a to_signals():
        n_domains = len({f.corr_group for f in r.findings})
        assert n_domains >= 3

    def test_projection_would_reach_reasoner_gate(self, rich_macos):
        # PROYECCIÓN B-052-P2: si cada corr_group emitiera su propia señal
        # primaria, ¿se alcanzaría el gate ≥3 del reasoner? Este test lo
        # afirma sobre el conteo de dominios (la lógica de emisión es de
        # B-052-P2, no de este fixture — aquí solo se prueba la precondición).
        r = MacOSForensicsAnalyzer().analyze(rich_macos)
        n_domains = len({f.corr_group for f in r.findings})
        assert n_domains >= 3, (
            "precondición del gate ≥3 del reasoner NO satisfecha: el split "
            "por dominio no produciría suficientes señales primarias"
        )
