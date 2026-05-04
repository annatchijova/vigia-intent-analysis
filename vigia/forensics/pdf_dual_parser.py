"""
vigia/forensics/pdf_dual_parser.py
====================================
Detector de evasión mediante divergencia de parsers PDF para VIGÍA.

Principio: CVE-2023-21608 y familia — exploits que funcionan en un parser
pero son "benignos" en otro. La divergencia estructural entre fitz y pypdf
es una señal activa de evasión, no ruido.

Un AV usando solo pypdf no detectaría el exploit.
VIGÍA detecta que fitz ve JavaScript y pypdf no → evasión deliberada.

Kimi fix aplicado:
- _calculate_entropy usa float internamente (OpenCV/numpy obliga)
  pero se convierte a Fraction antes de retornar
  Comentario: # HEURISTIC: entropy uses float internally, converted to Fraction

Invariantes:
- ParserResult es dataclass con structural_hash() para comparación
- DualParserAnalysis.evasion_likelihood es Fraction
- confidence_penalty es Fraction
- display usa int() truncado, nunca round()
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Optional


class ParserVerdict(Enum):
    CLEAN       = "clean"
    SUSPICIOUS  = "suspicious"
    MALICIOUS   = "malicious"
    PARSE_ERROR = "parse_error"


class AgreementStatus(Enum):
    CONSENSUS                  = "consensus"
    PARSER_DISAGREEMENT        = "parser_disagreement"
    PARSER_DIVERGENCE_CRITICAL = "divergence_critical"


# ─── Keywords por categoría de amenaza ───────────────────────────────────────

_JS_KEYWORDS: frozenset[str] = frozenset([
    "eval", "unescape", "String.fromCharCode",
    "this.exportDataObject", "app.launchURL",
    "/JavaScript", "/JS", "/OpenAction", "/AA",
])

_EXPLOIT_KEYWORDS: frozenset[str] = frozenset([
    "/RichMedia", "/EmbeddedFile", "/XFA",
    "AcroForm", "/Encrypt",
])

_STRUCTURAL_KEYWORDS: frozenset[str] = frozenset([
    "/ObjStm", "/XRef",
])


@dataclass
class ParserResult:
    parser_name:        str
    verdict:            ParserVerdict
    extracted_text_hash: str
    stream_count:       int
    js_detected:        bool
    embedded_files:     list[str]
    form_fields:        list[str]
    suspicious_keywords: list[str]
    raw_metadata:       dict
    entropy:            Fraction    # Fraction — nunca float en interfaz
    error:              Optional[str] = None

    def structural_hash(self) -> str:
        """Hash de estructura detectada para comparación entre parsers."""
        components = [
            str(self.js_detected),
            str(sorted(self.embedded_files)),
            str(sorted(self.suspicious_keywords)),
            str(self.stream_count),
        ]
        return hashlib.sha256("|".join(components).encode()).hexdigest()[:16]

    def display_entropy(self) -> str:
        """Entropy como string exacto — sin float display."""
        return f"{int(self.entropy * 100) / 100:.2f}"


@dataclass
class DualParserAnalysis:
    status:               AgreementStatus
    fitz_result:          Optional[ParserResult]
    pypdf_result:         Optional[ParserResult]
    disagreement_signals: list[str] = field(default_factory=list)
    evasion_indicators:   list[str] = field(default_factory=list)
    confidence_penalty:   Fraction  = Fraction(0)
    evasion_likelihood:   Fraction  = Fraction(0)
    forensic_note:        str       = ""
    alert_level:          str       = "LOW"
    recommendation:       str       = ""

    def display_evasion_pct(self) -> int:
        """Kimi fix: int() truncado."""
        return int(self.evasion_likelihood * 100)


# ─── Entropy ─────────────────────────────────────────────────────────────────

def _calculate_entropy(data: bytes) -> Fraction:
    """
    Calcula entropía de Shannon del contenido binario.
    # HEURISTIC: entropy uses float internally, converted to Fraction
    Kimi fix: comentario explícito sobre uso interno de float.
    """
    if not data:
        return Fraction(0)

    from collections import Counter
    import math

    counts = Counter(data)
    total  = len(data)

    # HEURISTIC: entropy uses float internally, converted to Fraction
    entropy_float = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy_float -= p * math.log2(p)

    # Convertir a Fraction con precisión de 2 decimales
    return Fraction(int(entropy_float * 100), 100)


# ─── Parsers ──────────────────────────────────────────────────────────────────

def _analyze_with_fitz(pdf_path: str) -> ParserResult:
    """Extracción con PyMuPDF (fitz). Captura estructura profunda via XRef."""
    try:
        import fitz  # type: ignore

        doc           = fitz.open(pdf_path)
        text_parts:   list[str] = []
        js_found      = False
        embedded:     list[str] = []
        suspicious:   list[str] = []
        stream_count  = 0

        for page in doc:
            text_parts.append(page.get_text("text"))

        xref_count = doc.xref_length()
        for xref in range(1, xref_count):
            try:
                obj_str = doc.xref_object(xref, compressed=False)
                if "stream" in obj_str:
                    stream_count += 1
                for kw in _JS_KEYWORDS:
                    if kw in obj_str:
                        js_found = True
                        suspicious.append(f"JS_KW:{kw}@xref{xref}")
                for kw in _EXPLOIT_KEYWORDS:
                    if kw in obj_str:
                        suspicious.append(f"EXPLOIT_KW:{kw}@xref{xref}")
                if "/EmbeddedFile" in obj_str:
                    embedded.append(f"embedded@xref{xref}")
            except Exception:
                suspicious.append(f"UNREADABLE_XREF:{xref}")

        full_text  = "\n".join(text_parts)
        text_hash  = hashlib.sha256(full_text.encode("utf-8", errors="replace")).hexdigest()
        metadata   = doc.metadata or {}
        doc.close()

        with open(pdf_path, "rb") as f:
            entropy = _calculate_entropy(f.read())

        verdict = _classify_verdict(suspicious, js_found)

        return ParserResult(
            parser_name="fitz",
            verdict=verdict,
            extracted_text_hash=text_hash,
            stream_count=stream_count,
            js_detected=js_found,
            embedded_files=embedded,
            form_fields=[],
            suspicious_keywords=suspicious,
            raw_metadata=metadata,
            entropy=entropy,
        )

    except ImportError:
        return ParserResult(
            parser_name="fitz", verdict=ParserVerdict.PARSE_ERROR,
            extracted_text_hash="", stream_count=0, js_detected=False,
            embedded_files=[], form_fields=[], suspicious_keywords=[],
            raw_metadata={}, entropy=Fraction(0), error="fitz_not_installed",
        )
    except Exception as exc:
        return ParserResult(
            parser_name="fitz", verdict=ParserVerdict.PARSE_ERROR,
            extracted_text_hash="", stream_count=0, js_detected=False,
            embedded_files=[], form_fields=[], suspicious_keywords=[],
            raw_metadata={}, entropy=Fraction(0), error=str(exc),
        )


def _analyze_with_pypdf(pdf_path: str) -> ParserResult:
    """Extracción con pypdf. Captura form fields y metadata diferente a fitz."""
    try:
        from pypdf import PdfReader  # type: ignore

        reader      = PdfReader(pdf_path)
        text_parts: list[str] = []
        js_found    = False
        suspicious: list[str] = []
        form_fields: list[str] = []

        for page in reader.pages:
            try:
                text_parts.append(page.extract_text() or "")
            except Exception:
                suspicious.append("PAGE_EXTRACT_ERROR")

        if reader.get_form_text_fields():
            form_fields = list(reader.get_form_text_fields().keys())

        metadata: dict = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                metadata[str(k)] = str(v)
                combined = f"{k}{v}"
                for kw in _JS_KEYWORDS | _EXPLOIT_KEYWORDS:
                    if kw in combined:
                        suspicious.append(f"METADATA_KW:{kw}")
                        if kw in _JS_KEYWORDS:
                            js_found = True

        try:
            named = reader.named_destinations
            if named:
                suspicious.append(f"NAMED_DESTS:{len(named)}")
        except Exception:
            pass

        full_text  = "\n".join(text_parts)
        text_hash  = hashlib.sha256(full_text.encode("utf-8", errors="replace")).hexdigest()

        with open(pdf_path, "rb") as f:
            entropy = _calculate_entropy(f.read())

        verdict = _classify_verdict(suspicious, js_found)

        return ParserResult(
            parser_name="pypdf",
            verdict=verdict,
            extracted_text_hash=text_hash,
            stream_count=len(reader.pages),
            js_detected=js_found,
            embedded_files=[],
            form_fields=form_fields,
            suspicious_keywords=suspicious,
            raw_metadata=metadata,
            entropy=entropy,
        )

    except ImportError:
        return ParserResult(
            parser_name="pypdf", verdict=ParserVerdict.PARSE_ERROR,
            extracted_text_hash="", stream_count=0, js_detected=False,
            embedded_files=[], form_fields=[], suspicious_keywords=[],
            raw_metadata={}, entropy=Fraction(0), error="pypdf_not_installed",
        )
    except Exception as exc:
        return ParserResult(
            parser_name="pypdf", verdict=ParserVerdict.PARSE_ERROR,
            extracted_text_hash="", stream_count=0, js_detected=False,
            embedded_files=[], form_fields=[], suspicious_keywords=[],
            raw_metadata={}, entropy=Fraction(0), error=str(exc),
        )


def _classify_verdict(suspicious: list[str], js_found: bool) -> ParserVerdict:
    if not suspicious and not js_found:
        return ParserVerdict.CLEAN
    exploit_signals = [s for s in suspicious if "EXPLOIT_KW" in s or "UNREADABLE" in s]
    if exploit_signals or (js_found and len(suspicious) > 2):
        return ParserVerdict.MALICIOUS
    return ParserVerdict.SUSPICIOUS


# ─── Divergence analysis ──────────────────────────────────────────────────────

def _compute_disagreement(
    fitz:  ParserResult,
    pypdf: ParserResult,
) -> tuple[list[str], list[str], Fraction]:
    signals: list[str] = []
    evasion: list[str] = []
    penalty = Fraction(0)

    if fitz.verdict != pypdf.verdict:
        signals.append(f"VERDICT_MISMATCH: fitz={fitz.verdict.value} pypdf={pypdf.verdict.value}")
        penalty += Fraction(3, 10)

    if (fitz.extracted_text_hash and pypdf.extracted_text_hash
            and fitz.extracted_text_hash != pypdf.extracted_text_hash):
        signals.append("TEXT_HASH_MISMATCH: parsers extract different text")
        evasion.append(
            "EVASION_INDICATOR: PDF uses differential encoding to evade "
            "scanners that use a single parser"
        )
        penalty += Fraction(4, 10)

    if fitz.js_detected != pypdf.js_detected:
        signals.append(
            f"JS_DETECTION_MISMATCH: fitz={fitz.js_detected} pypdf={pypdf.js_detected}"
        )
        evasion.append(
            "EVASION_INDICATOR: JavaScript visible only to one parser — "
            "documented evasion technique (CVE-2023-21608 family)"
        )
        penalty += Fraction(5, 10)

    stream_delta = abs(fitz.stream_count - pypdf.stream_count)
    if stream_delta > 2:
        signals.append(f"STREAM_COUNT_DELTA: {stream_delta} non-consensus streams")
        if stream_delta > 10:
            evasion.append(
                f"EVASION_INDICATOR: {stream_delta} streams invisible to pypdf — "
                f"possible /ObjStm compressed object streams for evasion"
            )
            penalty += Fraction(3, 10)

    if fitz.error and not pypdf.error:
        signals.append(f"FITZ_PARSE_FAILURE: {fitz.error}")
        evasion.append("EVASION_INDICATOR: PDF crafted to break fitz — targeted evasion")
        penalty += Fraction(2, 10)
    elif pypdf.error and not fitz.error:
        signals.append(f"PYPDF_PARSE_FAILURE: {pypdf.error}")
        evasion.append("EVASION_INDICATOR: PDF crafted to break pypdf — targeted evasion")
        penalty += Fraction(2, 10)

    if penalty > Fraction(1):
        penalty = Fraction(1)

    return signals, evasion, penalty


# ─── Entry point ─────────────────────────────────────────────────────────────

def analyze_pdf_dual(pdf_path: str) -> DualParserAnalysis:
    """
    Analiza el PDF con fitz y pypdf y detecta divergencias como señales activas.
    """
    fitz_result  = _analyze_with_fitz(pdf_path)
    pypdf_result = _analyze_with_pypdf(pdf_path)

    signals, evasion, penalty = _compute_disagreement(fitz_result, pypdf_result)

    evasion_score = penalty  # alias semántico

    if not signals:
        status = AgreementStatus.CONSENSUS
        alert  = "LOW"
        note   = "Both parsers agree. Standard analysis applicable."
    elif evasion:
        status = AgreementStatus.PARSER_DIVERGENCE_CRITICAL
        alert  = "CRITICAL"
        note   = (
            "FORENSIC ALERT: Active divergence detected. This PDF exhibits "
            "differential behavior between parsers — technique consistent with "
            "deliberate evasion exploits. Escalate to manual analysis with "
            "pdfid/pdf-parser."
        )
    else:
        status = AgreementStatus.PARSER_DISAGREEMENT
        alert  = "MEDIUM"
        note   = (
            "Minor parser disagreement. May indicate malformed PDF or "
            "non-standard structure. Review manually."
        )

    return DualParserAnalysis(
        status=status,
        fitz_result=fitz_result,
        pypdf_result=pypdf_result,
        disagreement_signals=signals,
        evasion_indicators=evasion,
        confidence_penalty=penalty,
        evasion_likelihood=evasion_score,
        forensic_note=note,
        alert_level=alert,
        recommendation=(
            "Submit to VirusTotal and analyze in sandboxed Adobe Reader."
            if evasion else ""
        ),
    )
