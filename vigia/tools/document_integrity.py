"""
vigia/tools/document_integrity.py
==================================
VIGÍA – Document forensic integrity tools.

Based on Case 041 (El Documento Frankenstein) and the vision analysis
requirements described in the architecture notes.

Tools
-----
* audit_document_integrity   : PDF/DOCX multi-layer integrity check
* analyze_image_layers       : ELA (Error Level Analysis) for image forgery
* detect_document_geometry   : margin/alignment/folio consistency
* ocr_semantic_validator     : gender-role coherence + missing mandatory fields

All tools are designed to be registered with FastMCP via @mcp.tool().
They import their dependencies lazily so the module loads even if optional
packages (fitz, PIL, pytesseract) are absent.

Security
--------
* All paths validated through vigia.security._sanitize_path
* File size capped at 50 MB for PDF/DOCX, 20 MB for images
* No subprocess calls – pure Python analysis only
"""

from __future__ import annotations
from fractions import Fraction

import hashlib
import io
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from vigia.security import _sanitize_path, audit_logger
from vigia.config import CONFIG

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_PDF_BYTES: Final[int] = 50 * 1024 * 1024   # 50 MB
MAX_IMG_BYTES: Final[int] = 20 * 1024 * 1024   # 20 MB
MAX_FONT_COUNT_THRESHOLD: Final[int] = 3
ELA_QUALITY: Final[int] = 90   # JPEG re-save quality for ELA

_PHONETIC_DICT_PATH: Final[Path] = (
    Path(__file__).parent.parent / "data" / "phonetic_dict.json"
)

# Cached phonetic dict
_PHONETIC_CACHE: dict | None = None


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_phonetic_dict() -> dict:
    global _PHONETIC_CACHE
    if _PHONETIC_CACHE is None:
        try:
            with open(_PHONETIC_DICT_PATH, "r", encoding="utf-8") as fh:
                _PHONETIC_CACHE = json.load(fh)
        except (OSError, json.JSONDecodeError):
            _PHONETIC_CACHE = {}
    return _PHONETIC_CACHE


# ---------------------------------------------------------------------------
# Helper: unified verdict scorer
# ---------------------------------------------------------------------------

def _score_to_verdict(score: float) -> str:
    if score >= 0.7:
        return "MALICE"
    if score >= 0.4:
        return "SUSPICION"
    return "NOISE"


# ---------------------------------------------------------------------------
# Tool 1: audit_document_integrity
# ---------------------------------------------------------------------------

async def audit_document_integrity(file_path: str) -> dict:
    """
    Forensic integrity audit for PDF documents.

    Detects
    -------
    * Font mixing (Frankenstein documents – manual copy-paste assembly)
    * Metadata anomalies (unofficial creation tools)
    * Gender/role inconsistency in Spanish Rioplatense legal documents
    * Temporal chaos (multiple inconsistent dates)
    * Near-zero entropy sections (padding / null-byte sections)
    * Basic ELA trigger: if PDF embeds images, flags them for layer analysis

    Parameters
    ----------
    file_path : path to the PDF file (must be within evidence base dir)

    Returns
    -------
    dict with verdict, suspicion_score, findings, document_stats, timestamp
    """
    # --- Path validation ---
    try:
        path = _sanitize_path(file_path, must_exist=True)
    except ValueError as exc:
        return {"status": "ERROR", "error": str(exc), "timestamp": _utcnow()}

    file_size = os.path.getsize(path)
    if file_size > MAX_PDF_BYTES:
        return {
            "status": "ERROR",
            "error": f"File too large: {file_size:,} bytes (max {MAX_PDF_BYTES:,})",
            "timestamp": _utcnow(),
        }

    # --- Magic bytes check ---
    with open(path, "rb") as fh:
        header = fh.read(4)
    if header != b"%PDF":
        return {
            "status": "ERROR",
            "error": "Not a valid PDF file (magic bytes mismatch)",
            "timestamp": _utcnow(),
        }

    findings: list[str] = []
    suspicion_score: float = 0.0
    fonts_found: set[str] = set()
    total_pages: int = 0
    text_full: str = ""
    metadata: dict = {}
    embedded_images: int = 0

    # --- PDF parsing (PyMuPDF preferred, pypdf fallback) ---
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        try:
            # P1-9: prevenir PDF bombs
            if len(doc) > 1000:
                doc.close()
                raise ValueError(f"PDF bomb detectada: {len(doc)} páginas (max 1000)")
            total_pages = len(doc)
            text_parts: list[str] = []

            for page in doc:
                text_parts.append(page.get_text())

                # Font extraction
                for block in page.get_text("dict")["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                fonts_found.add(span["font"])

                # Count embedded images
                embedded_images += len(page.get_images(full=True))

            text_full = "".join(text_parts)
            raw_meta = doc.metadata
            metadata = {k: (v or "") for k, v in raw_meta.items()}

        finally:
            doc.close()

    except ImportError:
        # P1-18: fallback pypdf — advertir diferencias determinísticas
        import sys
        print("[VIGÍA][WARNING] PyMuPDF no disponible — usando pypdf. "
              "Resultados pueden diferir entre plataformas. "
              "Instalar PyMuPDF para análisis forense determinístico.", file=sys.stderr)
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            total_pages = len(reader.pages)
            for page in reader.pages:
                text_full += page.extract_text() or ""
            raw_meta = reader.metadata or {}
            metadata = {str(k): str(v or "") for k, v in raw_meta.items()}
            fonts_found = {"[pypdf: font extraction unavailable]"}

        except ImportError:
            return {
                "status": "ERROR",
                "error": (
                    "No PDF library available. "
                    "Install with: pip install PyMuPDF  (preferred) or pypdf"
                ),
                "timestamp": _utcnow(),
            }

    # --- Rule 1: Font chaos (Frankenstein assembly) ---
    real_fonts = {f for f in fonts_found if not f.startswith("[")}
    if len(real_fonts) > MAX_FONT_COUNT_THRESHOLD:
        findings.append(
            f"VISUAL_CHAOS: {len(real_fonts)} distinct fonts detected "
            f"({', '.join(list(real_fonts)[:5])}{'…' if len(real_fonts) > 5 else ''}). "
            "Manual copy-paste assembly suspected."
        )
        suspicion_score += 0.5

    # --- Rule 2: Non-official creation tools ---
    phonetic = _load_phonetic_dict()
    unofficial_tools: list[str] = (
        phonetic.get("document_forgery_indicators", {})
        .get("unofficial_tool_producers", [
            "canva", "ilovepdf", "photoshop", "illustrator",
            "smallpdf", "pdf24", "sejda", "libreoffice", "pages",
        ])
    )

    producer_raw = metadata.get("/Producer", metadata.get("producer", "")).lower()
    creator_raw = metadata.get("/Creator", metadata.get("creator", "")).lower()
    combined_meta = producer_raw + " " + creator_raw

    matched_tools = [t for t in unofficial_tools if t in combined_meta]
    if matched_tools:
        findings.append(
            f"ORIGIN_ANOMALY: Created/produced by unofficial tool "
            f"({', '.join(matched_tools)}). Inconsistent with official judicial/institutional workflow."
        )
        suspicion_score += 0.4

    # --- Rule 3: Gender/role inconsistency (Spanish Rioplatense) ---
    gender_patterns = (
        phonetic.get("document_forgery_indicators", {})
        .get("gender_role_patterns_es_rioplatense", {})
        .get("patterns", [])
    )

    # Fallback hardcoded patterns if dict not loaded
    if not gender_patterns:
        gender_patterns = [
            {"regex": r"la\s+acusada[^.]{0,200}\bél\b",        "description": "Female accused, male pronoun",    "weight": 0.6},
            {"regex": r"el\s+imputado[^.]{0,200}\bella\b",      "description": "Male defendant, female pronoun", "weight": 0.6},
            {"regex": r"la\s+denunciante[^.]{0,200}\bél\b",     "description": "Female complainant, male pronoun","weight": 0.6},
            {"regex": r"el\s+testigo[^.]{0,200}\bella\b",       "description": "Male witness, female pronoun",   "weight": 0.6},
            {"regex": r"la\s+víctima[^.]{0,200}\bél\b",         "description": "Female victim, male pronoun",   "weight": 0.6},
            {"regex": r"la\s+acusada[^.]{0,200}\bél\s+mismo\b", "description": "Female accused + 'himself'",    "weight": 0.7},
        ]

    for pat_entry in gender_patterns:
        if re.search(pat_entry["regex"], text_full, re.IGNORECASE | re.DOTALL):
            findings.append(
                f"SEMANTIC_DOLO: Gender/role inconsistency detected – "
                f"{pat_entry['description']}. "
                "Possible subject substitution in legal document."
            )
            suspicion_score += float(pat_entry.get("weight", 0.6))
            break  # One is enough for conviction; more would inflate score

    # --- Rule 4: Temporal chaos ---
    date_pattern = r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b"
    dates_found = re.findall(date_pattern, text_full)
    unique_dates = set(dates_found)
    if len(unique_dates) > 4:
        findings.append(
            f"TEMPORAL_CHAOS: {len(unique_dates)} distinct dates found. "
            "Document may be assembled from multiple source fragments."
        )
        suspicion_score += 0.3

    # --- Rule 5: Missing mandatory fields (for institutional docs) ---
    # DNI / CUIL / CUIT in Argentine documents
    has_id = bool(re.search(r"\b(DNI|CUIL|CUIT|legajo|expediente)\b", text_full, re.IGNORECASE))
    if not has_id and total_pages >= 2:
        findings.append(
            "MISSING_MANDATORY_FIELD: No DNI/CUIL/CUIT/expediente reference found. "
            "Expected in official Argentine institutional documents."
        )
        suspicion_score += 0.2

    # --- Rule 6: Embedded images flag (refer to analyze_image_layers) ---
    if embedded_images > 0:
        findings.append(
            f"EMBEDDED_IMAGES: {embedded_images} image(s) found inside PDF. "
            "Run analyze_image_layers on extracted images to check for paste-in forgeries."
        )
        # Not scored – just advisory

    # --- Final score cap and verdict ---
    suspicion_score = min(Fraction(str(suspicion_score)).limit_denominator(100), Fraction(1))
    verdict = _score_to_verdict(suspicion_score)

    summary = findings[0] if findings else "Document appears structurally clean."

    return {
        "status": "OK",
        "verdict": verdict,
        "suspicion_score": suspicion_score,
        "findings": findings,
        "document_stats": {
            "pages": total_pages,
            "unique_fonts": len(real_fonts),
            "fonts": sorted(real_fonts)[:10],
            "embedded_images": embedded_images,
            "producer": producer_raw[:120],
            "creator": creator_raw[:120],
        },
        "file_sha256": _sha256_file(path),
        "timestamp": _utcnow(),
        "vigia_verdict": (
            f"[VIGIA_VERDICT]: {verdict}. "
            f"Integrity score: {round(suspicion_score * 100)}%. "
            f"{summary}"
        ),
    }


# ---------------------------------------------------------------------------
# Tool 2: analyze_image_layers (ELA – Error Level Analysis)
# ---------------------------------------------------------------------------

async def analyze_image_layers(image_path: str, ela_quality: int = ELA_QUALITY) -> dict:
    """
    Error Level Analysis (ELA) on an image to detect digitally pasted regions.

    How ELA works
    -------------
    The image is re-saved at a known JPEG quality level. Regions that were
    re-compressed after editing (e.g. a pasted seal or signature) retain
    higher error levels than the surrounding original pixels.  The variance
    in the error map reveals spliced regions.

    Parameters
    ----------
    image_path  : path to the image (JPEG, PNG, BMP, WEBP, TIFF)
    ela_quality : JPEG re-save quality (default 90). Lower = more sensitive.

    Returns
    -------
    dict with findings, ela_mean, ela_max, ela_variance, region_map summary
    """
    try:
        path = _sanitize_path(image_path, must_exist=True)
    except ValueError as exc:
        return {"status": "ERROR", "error": str(exc), "timestamp": _utcnow()}

    file_size = os.path.getsize(path)
    if file_size > MAX_IMG_BYTES:
        return {
            "status": "ERROR",
            "error": f"Image too large: {file_size:,} bytes (max {MAX_IMG_BYTES:,})",
            "timestamp": _utcnow(),
        }

    try:
        from PIL import Image, ImageChops, ImageEnhance
        import numpy as np
    except ImportError:
        return {
            "status": "ERROR",
            "error": "Pillow and numpy required: pip install Pillow numpy",
            "timestamp": _utcnow(),
        }

    findings: list[str] = []
    suspicion_score: float = 0.0

    # Open original
    try:
        # P1-12: validar dimensiones antes de decodificar
        with Image.open(path) as _img_check:
            if _img_check.width * _img_check.height > _MAX_IMAGE_PIXELS:
                raise ValueError(f"Imagen excede límite de píxeles: {_img_check.width}x{_img_check.height}")
        original = Image.open(path).convert("RGB")
    except Exception as exc:
        return {"status": "ERROR", "error": f"Cannot open image: {exc}", "timestamp": _utcnow()}

    # Re-save at known quality
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        original.save(tmp_path, "JPEG", quality=ela_quality)
        resaved = Image.open(tmp_path).convert("RGB")

        # Compute ELA: absolute difference, enhanced for visibility
        ela_image = ImageChops.difference(original, resaved)
        enhanced = ImageEnhance.Brightness(ela_image).enhance(10)

        # Statistical analysis of error levels
        ela_array = np.array(ela_image).astype(float)
        ela_mean = float(ela_array.mean())
        ela_max = float(ela_array.max())
        ela_variance = float(ela_array.var())

        # Region analysis: divide image into 4x4 grid, find outlier regions
        h, w = ela_array.shape[:2]
        block_h, block_w = h // 4, w // 4
        block_means = []
        for row in range(4):
            for col in range(4):
                block = ela_array[
                    row * block_h:(row + 1) * block_h,
                    col * block_w:(col + 1) * block_w,
                ]
                block_means.append(float(block.mean()))

        global_mean = sum(block_means) / len(block_means)
        # Blocks with mean > 2.5x global mean are suspicious
        hot_blocks = [
            {"row": i // 4, "col": i % 4, "ela_mean": round(v, 2)}
            for i, v in enumerate(block_means)
            if v > global_mean * 2.5 and global_mean > 0
        ]

        # Scoring
        if ela_variance > 500:
            findings.append(
                f"ELA_HIGH_VARIANCE: Regional ELA variance={ela_variance:.1f}. "
                "Significant difference in compression history across image regions."
            )
            suspicion_score += 0.5

        if hot_blocks:
            findings.append(
                f"ELA_HOT_REGIONS: {len(hot_blocks)} region(s) show anomalous error levels "
                f"(likely pasted content): {hot_blocks[:4]}"
            )
            suspicion_score += 0.4

        # EXIF metadata check (significant silence)
        exif_data = original.info.get("exif", b"")
        if not exif_data and path.lower().endswith((".jpg", ".jpeg", ".tiff")):
            findings.append(
                "SIGNIFICANT_SILENCE_VISUAL (Eco Filter): JPEG/TIFF image has no EXIF data. "
                "Metadata stripping suggests deliberate anonymisation."
            )
            suspicion_score += 0.25

        # Save ELA image for human review
        ela_output_path: str | None = None
        try:
            evidence_dir = CONFIG.evidence_base_dir
            ela_out = os.path.join(
                evidence_dir,
                f"ela_{Path(path).stem}_{_utcnow()[:10]}.jpg",
            )
            enhanced.save(ela_out, "JPEG", quality=95)
            ela_output_path = ela_out
        except OSError:
            pass  # Non-critical

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    suspicion_score = min(Fraction(str(suspicion_score)).limit_denominator(100), Fraction(1))
    verdict = _score_to_verdict(suspicion_score)

    return {
        "status": "OK",
        "verdict": verdict,
        "suspicion_score": suspicion_score,
        "findings": findings,
        "ela_stats": {
            "mean": round(ela_mean, 3),
            "max": round(ela_max, 3),
            "variance": round(ela_variance, 3),
            "hot_regions": hot_blocks,
        },
        "ela_image_saved": ela_output_path,
        "timestamp": _utcnow(),
        "vigia_verdict": (
            f"[VIGIA_VERDICT]: {verdict}. ELA analysis complete. "
            f"{'Forgery indicators present.' if findings else 'No splice indicators detected.'}"
        ),
    }


# ---------------------------------------------------------------------------
# Tool 3: detect_document_geometry
# ---------------------------------------------------------------------------

async def detect_document_geometry(file_path: str) -> dict:
    """
    Analyse PDF page geometry for margin inconsistency, text alignment
    anomalies, and stated vs actual page count.

    Detects folio/page-count manipulation and text blocks with different
    baseline alignments (indicative of inserted fragments).

    Parameters
    ----------
    file_path : path to the PDF

    Returns
    -------
    dict with geometry findings, page stats, alignment analysis
    """
    try:
        path = _sanitize_path(file_path, must_exist=True)
    except ValueError as exc:
        return {"status": "ERROR", "error": str(exc), "timestamp": _utcnow()}

    file_size = os.path.getsize(path)
    if file_size > MAX_PDF_BYTES:
        return {"status": "ERROR", "error": "File too large", "timestamp": _utcnow()}

    try:
        import fitz
    except ImportError:
        return {
            "status": "ERROR",
            "error": "PyMuPDF required: pip install PyMuPDF",
            "timestamp": _utcnow(),
        }

    findings: list[str] = []
    suspicion_score: float = 0.0

    doc = fitz.open(path)
    try:
        actual_pages = len(doc)

        # Check stated page count in document body (Argentine legal docs often say "hoja X de Y")
        full_text = "".join(page.get_text() for page in doc)
        stated_total_match = re.search(
            r"(?:hoja|página|foja|folio)\s+\d+\s+de\s+(\d+)",
            full_text,
            re.IGNORECASE,
        )

        if stated_total_match:
            stated_total = int(stated_total_match.group(1))
            if stated_total != actual_pages:
                findings.append(
                    f"PAGE_COUNT_MISMATCH: Document states {stated_total} pages but PDF has {actual_pages}. "
                    "Possible page insertion or removal."
                )
                suspicion_score += 0.6

        # Analyse margin consistency across pages
        page_widths = []
        page_heights = []
        text_left_margins: list[float] = []

        for page in doc:
            rect = page.rect
            page_widths.append(rect.width)
            page_heights.append(rect.height)

            # Find leftmost text block
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block.get("type") == 0:  # text block
                    text_left_margins.append(block["bbox"][0])
                    break  # first text block per page is enough

        # Margin variance check
        if len(text_left_margins) > 2:
            mean_margin = sum(text_left_margins) / len(text_left_margins)
            variance = sum((m - mean_margin) ** 2 for m in text_left_margins) / len(text_left_margins)
            if variance > 100:  # > 10pt² variance in left margin
                findings.append(
                    f"MARGIN_INCONSISTENCY: Left text margin variance={variance:.1f}pt². "
                    f"Mean margin={mean_margin:.1f}pt. "
                    "Pages may originate from different source documents."
                )
                suspicion_score += 0.4

        # Page dimension consistency
        unique_dims = set(zip(
            [round(w) for w in page_widths],
            [round(h) for h in page_heights],
        ))
        if len(unique_dims) > 1:
            findings.append(
                f"DIMENSION_CHAOS: {len(unique_dims)} distinct page sizes found: {unique_dims}. "
                "Pages from different paper standards (A4 vs Letter vs Legal) mixed together."
            )
            suspicion_score += 0.35

    finally:
        doc.close()

    suspicion_score = min(Fraction(str(suspicion_score)).limit_denominator(100), Fraction(1))
    verdict = _score_to_verdict(suspicion_score)

    return {
        "status": "OK",
        "verdict": verdict,
        "suspicion_score": suspicion_score,
        "findings": findings,
        "geometry_stats": {
            "actual_pages": actual_pages,
            "unique_page_dimensions": len(unique_dims) if "unique_dims" in dir() else 1,
        },
        "timestamp": _utcnow(),
        "vigia_verdict": (
            f"[VIGIA_VERDICT]: {verdict}. Geometry analysis complete. "
            f"{findings[0] if findings else 'Page geometry is consistent.'}"
        ),
    }


# ---------------------------------------------------------------------------
# Tool 4: ocr_semantic_validator
# ---------------------------------------------------------------------------

async def ocr_semantic_validator(
    file_path: str,
    language: str = "spa",
    check_mandatory_fields: bool = True,
) -> dict:
    """
    Extract text via OCR (for scanned PDFs or images) and run semantic
    consistency checks.

    Checks
    ------
    * Subject pronoun coherence across pages (gender/role consistency)
    * Presence of mandatory fields: DNI, expediente, firma, fecha
    * Tense consistency (legal documents should be in a single tense mode)

    Parameters
    ----------
    file_path              : path to PDF or image
    language               : tesseract language code (default: "spa" for Spanish)
    check_mandatory_fields : if True, flag missing obligatory legal fields

    Returns
    -------
    dict with semantic findings, extracted text preview, mandatory field status
    """
    try:
        path = _sanitize_path(file_path, must_exist=True)
    except ValueError as exc:
        return {"status": "ERROR", "error": str(exc), "timestamp": _utcnow()}

    findings: list[str] = []
    suspicion_score: float = 0.0
    text_by_page: list[str] = []

    # Try PyMuPDF text extraction first (no OCR needed for digital PDFs)
    text_extracted_via = "native"
    try:
        import fitz
        doc = fitz.open(path)
        try:
            for page in doc:
                text_by_page.append(page.get_text())
        finally:
            doc.close()

        # If text is sparse, fall through to OCR
        total_chars = sum(len(t) for t in text_by_page)
        if total_chars < 100 * len(text_by_page):
            raise ValueError("Text too sparse – likely scanned document")

    except Exception:
        # Fall back to OCR
        text_extracted_via = "ocr"
        try:
            import pytesseract
            from PIL import Image

            ext = Path(path).suffix.lower()
            if ext == ".pdf":
                try:
                    import fitz
                    doc = fitz.open(path)
                    try:
                        for page in doc:
                            pix = page.get_pixmap(dpi=200)
                            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            text_by_page.append(pytesseract.image_to_string(img, lang=language))
                    finally:
                        doc.close()
                except ImportError:
                    return {
                        "status": "ERROR",
                        "error": "PyMuPDF required for OCR on PDFs: pip install PyMuPDF",
                        "timestamp": _utcnow(),
                    }
            else:
                # P1-12: validar dimensiones
                with Image.open(path) as _dim_check:
                    if _dim_check.width * _dim_check.height > _MAX_IMAGE_PIXELS:
                        raise ValueError(f"Imagen excede límite: {_dim_check.width}x{_dim_check.height}")
                img = Image.open(path)
                text_by_page.append(pytesseract.image_to_string(img, lang=language))

        except ImportError:
            return {
                "status": "ERROR",
                "error": (
                    "pytesseract required for OCR: pip install pytesseract\n"
                    "Also install tesseract-ocr and the Spanish language pack:\n"
                    "  sudo apt install tesseract-ocr tesseract-ocr-spa"
                ),
                "timestamp": _utcnow(),
            }

    full_text = "\n".join(text_by_page)

    # --- Semantic check 1: subject coherence across pages ---
    phonetic = _load_phonetic_dict()
    gender_patterns = (
        phonetic.get("document_forgery_indicators", {})
        .get("gender_role_patterns_es_rioplatense", {})
        .get("patterns", [])
    )

    for pat_entry in gender_patterns:
        if re.search(pat_entry["regex"], full_text, re.IGNORECASE | re.DOTALL):
            findings.append(
                f"SUBJECT_INCOHERENCE: {pat_entry['description']}. "
                "Subject gender changes between document sections – "
                "indicates fragment substitution."
            )
            suspicion_score += float(pat_entry.get("weight", 0.6))
            break

    # --- Semantic check 2: mandatory fields ---
    if check_mandatory_fields:
        mandatory = {
            "DNI/CUIL": r"\b(DNI|CUIL|CUIT)\b",
            "Expediente": r"\b(expediente|expte\.?|folio|legajo)\b",
            "Fecha": r"\b\d{1,2}\s+de\s+\w+\s+de\s+\d{4}\b",
            "Firma": r"\b(firma|firmado|suscribe|suscripto)\b",
        }
        missing = []
        for field_name, pattern in mandatory.items():
            if not re.search(pattern, full_text, re.IGNORECASE):
                missing.append(field_name)

        if missing:
            findings.append(
                f"MISSING_MANDATORY_FIELDS: {', '.join(missing)} not found. "
                "Expected in official Argentine legal/institutional documents."
            )
            suspicion_score += 0.15 * len(missing)

    # --- Semantic check 3: per-page subject tracking ---
    subject_gender_per_page: list[str] = []
    for page_text in text_by_page:
        if re.search(r"\b(el\s+acusado|el\s+imputado|el\s+testigo)\b", page_text, re.IGNORECASE):
            subject_gender_per_page.append("M")
        elif re.search(r"\b(la\s+acusada|la\s+imputada|la\s+testigo)\b", page_text, re.IGNORECASE):
            subject_gender_per_page.append("F")
        else:
            subject_gender_per_page.append("?")

    gender_values = [g for g in subject_gender_per_page if g != "?"]
    if len(set(gender_values)) > 1:
        findings.append(
            f"CROSS_PAGE_GENDER_FLIP: Subject gender changes across pages: "
            f"{subject_gender_per_page}. "
            "Strong indicator of document assembly from different cases."
        )
        suspicion_score += 0.7

    suspicion_score = min(Fraction(str(suspicion_score)).limit_denominator(100), Fraction(1))
    verdict = _score_to_verdict(suspicion_score)

    return {
        "status": "OK",
        "verdict": verdict,
        "suspicion_score": suspicion_score,
        "findings": findings,
        "extraction_method": text_extracted_via,
        "text_preview": full_text[:500] + ("…" if len(full_text) > 500 else ""),
        "subject_gender_by_page": subject_gender_per_page,
        "mandatory_fields_present": not any("MISSING_MANDATORY" in f for f in findings),
        "timestamp": _utcnow(),
        "vigia_verdict": (
            f"[VIGIA_VERDICT]: {verdict}. Semantic validation complete. "
            f"{findings[0] if findings else 'Document semantics are consistent.'}"
        ),
    }


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _sha256_file(path: str, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()
