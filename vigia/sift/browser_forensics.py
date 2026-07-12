"""
vigia/sift/browser_forensics.py

Analiza artefactos de navegador: historial, downloads, cookies, cache.
Detecta descarga de herramientas de ataque, navegación a dominios C2,
y correlación con actividad de red.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

import logging
import ntpath
import posixpath
import sqlite3
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._sql_utils import safe_sqlite_connect

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

TOOL_NAME = "BROWSER_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(65, 100)

# Nombres de base de datos por navegador
_CHROMIUM_HISTORY = "History"      # Chrome/Edge/Brave: downloads + urls en un solo SQLite
_FIREFOX_PLACES = "places.sqlite"  # Firefox: moz_places (+ moz_annos para downloads)

# Dominios sospechosos asociados a descarga de herramientas de ataque
MALICIOUS_DOMAINS = {
    "github.com/mimikatz", "github.com/gentilkiwi",
    "download.sysinternals.com",  # Legítimo pero usado en ataques
}

# Extensiones de archivo sospechosas en downloads
SUSPICIOUS_EXTENSIONS = {".exe",".dll",".ps1",".bat",".cmd",".vbs",".js",".hta"}


@dataclass
class BrowserDownloadRecord:
    url: str
    filename: str
    download_time: str
    file_size: int
    target_path: str
    danger_type: str
    opened: bool


@dataclass
class BrowserHistoryRecord:
    url: str
    title: str
    visit_time: str
    visit_count: int
    transition_type: str


@dataclass
class BrowserAnalysisResult:
    source_profile: str
    total_downloads: int
    suspicious_downloads: List[Dict[str, Any]]
    c2_navigation: List[Dict[str, Any]]
    credential_access: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)
    # True si el perfil contenía bases de datos que NO se pudieron parsear
    # (corruptas/bloqueadas) — distinto de "perfil sin actividad".
    unanalyzed: bool = False
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.c2_navigation:
            z = Fraction(30, 10)
        elif len(self.suspicious_downloads) >= 3:
            z = Fraction(25, 10)
        elif self.suspicious_downloads:
            z = Fraction(18, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "source_profile": self.source_profile,
                "total_downloads": self.total_downloads,
                "suspicious_count": len(self.suspicious_downloads),
                "c2_count": len(self.c2_navigation),
                "artifact_type": "browser",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                # Ya no es stub: parseo SQLite real. unanalyzed marca el caso
                # en que había DBs presentes pero ilegibles (→ ABSTAIN, no limpio).
                "unanalyzed": self.unanalyzed,
                "analysis_notes": self.analysis_notes,
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_downloads
                ) | set(
                    c.get("type", "UNKNOWN") for c in self.c2_navigation
                ))),
            }
        )


class BrowserForensicsEngine:
    """Analiza perfiles de Chrome/Edge/Firefox."""

    def analyze_profile(
        self,
        profile_path: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> BrowserAnalysisResult:
        """
        Parseo real de perfiles Chromium (History) y Firefox (places.sqlite).

        Las bases se abren vía safe_sqlite_connect (B-071): copia la familia
        db + -wal/-shm/-journal a un working dir efímero y abre la COPIA.
        La evidencia nunca se toca Y el WAL no-checkpointeado SÍ se lee —
        immutable=1 lo ignoraba (mismo FN cuantificado en Safari/tuck-2019:
        hasta el 100% de la señal invisible; docs/SAFARI_WAL_FIX_ANALYSIS.md).
        """
        p = Path(profile_path).resolve()
        suspicious: List[Dict[str, Any]] = []
        c2_nav: List[Dict[str, Any]] = []
        cred_access: List[Dict[str, Any]] = []
        notes: List[str] = []
        unanalyzed = False
        total_downloads = 0

        if not p.exists():
            return BrowserAnalysisResult(
                source_profile=str(p), total_downloads=0,
                suspicious_downloads=[], c2_navigation=[], credential_access=[],
            )

        # Localizar las bases de datos (perfil como directorio o archivo directo)
        chromium_db = self._locate_db(p, _CHROMIUM_HISTORY)
        firefox_db = self._locate_db(p, _FIREFOX_PLACES)

        if chromium_db is not None:
            try:
                dl, hist = self._parse_chromium(chromium_db)
                total_downloads += len(dl)
                self._classify(dl, hist, suspicious, c2_nav)
                notes.append(f"chromium: {len(dl)} downloads, {len(hist)} urls")
            except sqlite3.DatabaseError as e:
                unanalyzed = True
                notes.append(f"UNANALYZED_ARTIFACT: Chromium History ilegible: {e}")
                logger.error("[BROWSER] Chromium History ilegible %s: %s", chromium_db, e)

        if firefox_db is not None:
            try:
                dl, hist = self._parse_firefox(firefox_db)
                total_downloads += len(dl)
                self._classify(dl, hist, suspicious, c2_nav)
                notes.append(f"firefox: {len(dl)} downloads, {len(hist)} urls")
            except sqlite3.DatabaseError as e:
                unanalyzed = True
                notes.append(f"UNANALYZED_ARTIFACT: Firefox places.sqlite ilegible: {e}")
                logger.error("[BROWSER] Firefox places ilegible %s: %s", firefox_db, e)

        if chromium_db is None and firefox_db is None:
            notes.append("No se encontró History (Chromium) ni places.sqlite (Firefox).")

        if chain:
            chain.acquire(b"BROWSER_ANALYSIS", "BROWSER_FORENSICS", timestamp_utc)

        # composite_score: escala con la severidad de los hallazgos, acotado [0,1]
        raw = Fraction(len(c2_nav) * 5 + len(suspicious) * 3, 10)
        composite = min(raw, Fraction(1, 1))

        return BrowserAnalysisResult(
            source_profile=str(p),
            total_downloads=total_downloads,
            suspicious_downloads=suspicious,
            c2_navigation=c2_nav,
            credential_access=cred_access,
            composite_score=composite,
            unanalyzed=unanalyzed,
            analysis_notes=notes,
        )

    # ── Localización y apertura read-only ──────────────────────────────────

    @staticmethod
    def _locate_db(path: Path, db_name: str) -> Optional[Path]:
        """Devuelve la ruta a db_name si path es ese archivo o lo contiene."""
        if path.is_file():
            return path if path.name == db_name else None
        candidate = path / db_name
        return candidate if candidate.is_file() else None

    @staticmethod
    def _connect_evidence(db_path: Path) -> sqlite3.Connection:
        """Abre la DB de evidencia vía safe_sqlite_connect (working copy con
        WAL aplicado, evidencia intacta). Un fallo de apertura a nivel OS
        (retorno None) se eleva como DatabaseError para que analyze_profile
        lo marque UNANALYZED — nunca 'perfil limpio'."""
        conn = safe_sqlite_connect(db_path, "BROWSER", logger)
        if conn is None:
            raise sqlite3.DatabaseError(
                f"cannot open working copy of evidence DB: {db_path}"
            )
        return conn

    # ── Parsers por navegador ──────────────────────────────────────────────

    def _parse_chromium(self, db_path: Path):
        """
        Chromium: downloads (+ downloads_url_chains para la URL de origen) y
        urls (historial). Devuelve (downloads, history) como listas de dicts.
        """
        downloads: List[Dict[str, Any]] = []
        history: List[Dict[str, Any]] = []
        conn = self._connect_evidence(db_path)
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            if self._has_table(cur, "downloads"):
                has_chains = self._has_table(cur, "downloads_url_chains")
                url_expr = (
                    "(SELECT url FROM downloads_url_chains c "
                    " WHERE c.id = d.id ORDER BY c.chain_index LIMIT 1)"
                    if has_chains else "d.tab_url"
                )
                for row in cur.execute(
                    f"SELECT d.id AS id, d.target_path AS target_path, "
                    f"d.total_bytes AS total_bytes, d.opened AS opened, "
                    f"d.danger_type AS danger_type, {url_expr} AS url FROM downloads d"
                ):
                    target = row["target_path"] or ""
                    downloads.append({
                        "url": row["url"] or "",
                        "filename": self._basename(target),
                        "target_path": target,
                        "total_bytes": row["total_bytes"] or 0,
                        "opened": bool(row["opened"]),
                        "danger_type": row["danger_type"],
                    })
            if self._has_table(cur, "urls"):
                for row in cur.execute(
                    "SELECT url, title, visit_count FROM urls"
                ):
                    history.append({
                        "url": row["url"] or "",
                        "title": row["title"] or "",
                        "visit_count": row["visit_count"] or 0,
                    })
        finally:
            conn.close()
        return downloads, history

    def _parse_firefox(self, db_path: Path):
        """
        Firefox: moz_places (historial) y downloads vía moz_annos
        (destinationFileURI / downloads/destinationFileURI). Best-effort.
        """
        downloads: List[Dict[str, Any]] = []
        history: List[Dict[str, Any]] = []
        conn = self._connect_evidence(db_path)
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            if self._has_table(cur, "moz_places"):
                for row in cur.execute(
                    "SELECT url, title, visit_count FROM moz_places"
                ):
                    history.append({
                        "url": row["url"] or "",
                        "title": row["title"] or "",
                        "visit_count": row["visit_count"] or 0,
                    })
            # Descargas modernas: moz_annos con anno 'downloads/destinationFileURI'
            if self._has_table(cur, "moz_annos") and self._has_table(cur, "moz_places"):
                try:
                    for row in cur.execute(
                        "SELECT p.url AS url, a.content AS dest "
                        "FROM moz_annos a JOIN moz_places p ON a.place_id = p.id "
                        "JOIN moz_anno_attributes t ON a.anno_attribute_id = t.id "
                        "WHERE t.name = 'downloads/destinationFileURI'"
                    ):
                        dest = row["dest"] or ""
                        downloads.append({
                            "url": row["url"] or "",
                            "filename": self._basename(dest),
                            "target_path": dest,
                            "total_bytes": 0,
                            "opened": False,
                            "danger_type": None,
                        })
                except sqlite3.DatabaseError:
                    pass  # esquema antiguo sin esa anno — historial ya capturado
        finally:
            conn.close()
        return downloads, history

    @staticmethod
    def _basename(target: str) -> str:
        """
        Nombre de archivo desde un target_path que puede ser Windows (\\) o
        POSIX (/). La evidencia Windows se analiza sobre SIFT (Linux), así que
        no se puede depender de os.path — se prueban ambos separadores.
        """
        if not target:
            return ""
        return ntpath.basename(target) or posixpath.basename(target)

    @staticmethod
    def _has_table(cur: sqlite3.Cursor, name: str) -> bool:
        row = cur.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        return row is not None

    # ── Clasificación ──────────────────────────────────────────────────────

    def _classify(self, downloads, history, suspicious, c2_nav) -> None:
        """Aplica _is_suspicious_download y detección de dominios C2."""
        for d in downloads:
            if self._is_suspicious_download(d["url"], d["filename"]):
                suspicious.append({
                    "type": "SUSPICIOUS_DOWNLOAD",
                    "url": d["url"], "filename": d["filename"],
                    "target_path": d["target_path"], "opened": d["opened"],
                })
        for h in history:
            url_lower = h["url"].lower()
            for domain in MALICIOUS_DOMAINS:
                if domain in url_lower:
                    c2_nav.append({
                        "type": "C2_NAVIGATION",
                        "url": h["url"], "title": h["title"],
                        "visit_count": h["visit_count"], "matched_domain": domain,
                    })
                    break

    def _is_suspicious_download(self, url: str, filename: str) -> bool:
        """Determina si una descarga es sospechosa."""
        url_lower = url.lower()
        filename_lower = filename.lower()

        # Herramientas de ataque conocidas
        for domain in MALICIOUS_DOMAINS:
            if domain in url_lower:
                return True

        # Extensiones ejecutables
        if any(filename_lower.endswith(ext) for ext in SUSPICIOUS_EXTENSIONS):
            return True

        return False
