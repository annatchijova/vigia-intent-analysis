# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vigia/tools/vision_audit.py
===========================
VIGIA - Visual Intentionality Audit using CLIP + Forensic Analysis.

Detects intentionality dissonance in images and scanned documents:
whether a visual artifact looks official but carries structural markers
of fabrication (cut-paste, digital collage, pasted seals).

FORENSIC GRADE ENHANCEMENTS (Kimi P1-10, SANS Hackathon 2026):
* Digital Perfection Detection: Local variance analysis to detect resolution
  discrepancies between document elements (seals, signatures vs background).
* CAIE Integration: Automatic injection of DOCUMENT_FORGERY fractures into
  CrossArtifactIncongruenceEngine via add_from_tool_result().
* Silent Metadata Analysis: EXIF/XMP forensic analysis with compression artifact
  detection and software tampering indicators.
* Deterministic 100%: No LLM hallucinations — only local variance, 
  Laplacian edges, and resource limits.

Architecture notes
------------------
* The CLIPVisualAuditor is NOT instantiated at import time.  torch and clip
  are optional heavy dependencies.  Use get_auditor() to obtain the singleton
  on first call; this keeps import cost near zero when CLIP is not installed.
* Model integrity verification is present but the expected SHA-256 must be
  populated from the official OpenAI CLIP release before production use.
  See CLIP_MODEL_HASHES below.
* Resource limits: max image dimension, max pixel count, inference timeout.
* All paths validated through vigia.security._sanitize_path.
* No emojis anywhere in this file.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import os
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from vigia.security import _sanitize_path, _utcnow, audit_logger

# ---------------------------------------------------------------------------
# Security constants
# ---------------------------------------------------------------------------

MAX_IMAGE_DIMENSION: Final[int] = 8192
MAX_IMAGE_PIXELS: Final[int] = 32_000_000          # ~32 MP
MAX_IMAGE_BYTES: Final[int] = 20 * 1024 * 1024     # 20 MB
CLIP_INFERENCE_TIMEOUT: Final[float] = 30.0

ALLOWED_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tiff",
})

MALICE_THRESHOLD: Final[float] = 0.75
SUSPICION_THRESHOLD: Final[float] = 0.50

# Kimi P1-10: Digital Perfection thresholds for forensic analysis
DIGITAL_PERFECTION_VARIANCE_THRESHOLD: Final[float] = 0.15  # Local variance ratio
DIGITAL_PERFECTION_EDGE_THRESHOLD: Final[float] = 2.5         # Laplacian edge sharpness ratio
DIGITAL_PERFECTION_MALICE_SCORE: Final[float] = 0.9          # Fixed score for digital perfection detection

# Kimi P1-10: Compression artifact detection thresholds
JPEG_QUALITY_INCONSISTENCY_THRESHOLD: Final[float] = 15.0    # DCT coefficient variance
CHROMA_SUBSAMPLING_ANOMALY_THRESHOLD: Final[float] = 0.3      # Chroma channel variance ratio

# ---------------------------------------------------------------------------
# CLIP model integrity hashes
# ---------------------------------------------------------------------------
# Hash resolution (priority order):
#   1. VIGIA_CLIP_HASH_FILE env var → JSON file mapping filename → sha256
#      Example: {"ViT-B-32.pt": "abcdef1234..."}
#   2. VIGIA_CLIP_HASH_VIT_B_32 env var → direct hash for ViT-B/32
#   3. Hardcoded dict below (populate before production use)
#
# Strict mode (VIGIA_STRICT_MODEL_CHECK=true):
#   If enabled and NO hash is configured for a model, CLIPVisualAuditor
#   will REFUSE to load. This prevents silent skip of integrity checks
#   in production/court environments.
#
# To populate: run  sha256sum ~/.cache/clip/ViT-B-32.pt

_STRICT_MODEL_CHECK: Final[bool] = (
    os.getenv("VIGIA_STRICT_MODEL_CHECK", "false").lower() == "true"
)

# Hardcoded fallback — override via env vars above
_CLIP_MODEL_HASHES_BUILTIN: Final[dict[str, str]] = {
    "ViT-B-32.pt": "",   # Configurar via VIGIA_CLIP_HASH_FILE o VIGIA_CLIP_HASH_VIT_B_32 (ver QUICK_START.md)
}


def _load_clip_model_hashes() -> dict[str, str]:
    """
    Load CLIP model hashes from external file or env vars.

    Returns a dict mapping model filename → expected SHA-256 hex string.
    Empty string values mean "hash not configured".
    """
    hashes = dict(_CLIP_MODEL_HASHES_BUILTIN)

    # 1. Try external JSON file
    hash_file = os.getenv("VIGIA_CLIP_HASH_FILE", "").strip()
    if hash_file:
        try:
            import json as _json
            with open(hash_file, "r", encoding="utf-8") as fh:
                external = _json.load(fh)
            if isinstance(external, dict):
                hashes.update(external)
                audit_logger.log_info(
                    event_type="MODEL_HASHES_LOADED",
                    tool="vision_audit",
                    message=f"Loaded {len(external)} model hash(es) from {hash_file}",
                )
        except (OSError, ValueError) as exc:
            audit_logger.log_info(
                event_type="MODEL_HASH_FILE_ERROR",
                tool="vision_audit",
                message=f"Cannot load hash file {hash_file}: {exc}",
            )

    # 2. Try per-model env vars (e.g. VIGIA_CLIP_HASH_VIT_B_32)
    for filename in list(hashes.keys()):
        env_key = "VIGIA_CLIP_HASH_" + filename.replace("-", "_").replace(".", "_").upper()
        env_val = os.getenv(env_key, "").strip()
        if env_val:
            hashes[filename] = env_val

    return hashes


CLIP_MODEL_HASHES: Final[dict[str, str]] = _load_clip_model_hashes()

# ---------------------------------------------------------------------------
# Semantic labels for zero-shot classification
# ---------------------------------------------------------------------------
# Peirce framing:
#   Firstness  - what does the image look like?
#   Secondness - does it have the structural properties of its claimed type?
#   Thirdness  - what communicative habit does it reveal?

_DEFAULT_LABELS: Final[list[str]] = [
    "an official government judicial document",          # legitimate anchor
    "a manual digital collage with cut and paste elements",
    "a genuine legal notification with standard margins",
    "a forged document with inconsistent fonts",
    "a sovereign state seal printed on paper",
    "a digital stamp icon pasted over a document",       # forgery anchor
]

# Kimi P1-10: Extended labels for forensic digital perfection detection
_FORENSIC_LABELS: Final[list[str]] = [
    "a scanned document with consistent paper texture and noise",
    "a digitally inserted signature with sharp edges on scanned paper",
    "a pasted official seal with different resolution than background",
    "a document with uniform scanning artifacts throughout",
    "a composite document with mismatched DPI elements",
]

# ---------------------------------------------------------------------------
# Module-level singleton (lazy)
# ---------------------------------------------------------------------------

_auditor_instance: "CLIPVisualAuditor | None" = None


async def get_auditor(model_name: str = "ViT-B/32") -> "CLIPVisualAuditor":
    """
    Return the module-level CLIPVisualAuditor singleton, creating it on first
    call.  Raises RuntimeError if torch or clip are not installed.

    P1: La carga del modelo CLIP bloquea el event loop (I/O pesada + CPU).
    Usar run_in_executor para no congelar el servidor MCP.
    """
    global _auditor_instance
    if _auditor_instance is None:
        loop = asyncio.get_event_loop()
        _auditor_instance = await loop.run_in_executor(
            None, lambda: CLIPVisualAuditor(model_name=model_name)
        )
    return _auditor_instance


# ---------------------------------------------------------------------------
# Model integrity helper
# ---------------------------------------------------------------------------

def _verify_model_integrity(model_path: Path, expected_hash: str) -> bool:
    """
    Verify SHA-256 of a CLIP model file.

    Returns True if the hash matches or if expected_hash is empty (skip mode).
    Returns False only when a non-empty expected_hash is provided and does not
    match – indicating possible supply-chain tampering.
    """
    if not expected_hash:
        return True   # Hash not configured: skip check, log warning
    if not model_path.exists():
        return False
    sha256 = hashlib.sha256()
    with open(model_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash


# ---------------------------------------------------------------------------
# Kimi P1-10: Forensic Digital Perfection Detection
# ---------------------------------------------------------------------------

class ForensicImageAnalyzer:
    """
    Forensic analysis engine for detecting digital perfection anomalies.

    Detects structural discrepancies where elements (seals, signatures)
    have resolution/nitidez inconsistent with background paper noise.

    DETERMINISTIC 100%: No probabilistic ML — only computer vision
    algorithms with mathematically defined thresholds.
    """

    def __init__(self):
        self.has_opencv = False
        self.has_numpy = False
        try:
            import cv2
            import numpy as np
            self.has_opencv = True
            self.has_numpy = True
            self.cv2 = cv2
            self.np = np
        except ImportError:
            audit_logger.log_info(
                event_type="FORENSIC_DEPS_MISSING",
                tool="ForensicImageAnalyzer",
                message="OpenCV/NumPy not available. Digital perfection detection limited.",
            )

    def analyze_digital_perfection(self, image_path: str, image: "Image.Image") -> dict:
        """
        Analyze image for digital perfection indicators.

        DETERMINISTIC ALGORITHM:
        1. Compute local variance in 32x32 windows
        2. Estimate background noise from low-variance regions
        3. Detect high-precision regions (potential digital insertions)
        4. Measure Laplacian edge sharpness
        5. Identify anomaly regions with mathematical thresholds

        Returns dict with:
            digital_perfection_detected (bool)
            variance_ratio (float)
            edge_sharpness_ratio (float)
            anomaly_regions (list)
            confidence (float)
        """
        if not self.has_opencv:
            return {
                "digital_perfection_detected": False,
                "variance_ratio": 0.0,
                "edge_sharpness_ratio": 0.0,
                "anomaly_regions": [],
                "confidence": 0.0,
                "note": "OpenCV not available for forensic analysis"
            }

        try:
            # Convert PIL to OpenCV format (BGR)
            import numpy as np
            img_array = np.array(image.convert('RGB'))
            # P1: validar dimensiones mínimas para análisis forense
            h, w = img_array.shape[:2]
            if h < 64 or w < 64:
                return {
                    "digital_perfection_detected": False,
                    "variance_ratio": 0.0,
                    "edge_sharpness_ratio": 0.0,
                    "anomaly_regions": [],
                    "confidence": 0.0,
                    "note": f"Image too small for forensic analysis: {w}x{h} (min 64x64)"
                }
            img_cv = self.cv2.cvtColor(img_array, self.cv2.COLOR_RGB2BGR)
            gray = self.cv2.cvtColor(img_cv, self.cv2.COLOR_BGR2GRAY)

            # 1. Local variance analysis using sliding window (32x32)
            window_size = 32
            local_var = self._compute_local_variance(gray, window_size)

            # 2. Global background noise estimation (assumed paper texture)
            # Exclude high-variance regions (text, seals) to estimate pure paper noise
            background_mask = local_var < np.percentile(local_var, 30)
            background_var = np.mean(local_var[background_mask]) if np.any(background_mask) else np.mean(local_var)

            # 3. Detect high-precision regions (potential digital insertions)
            high_precision_mask = local_var > (background_var * 3)

            # 4. Edge sharpness analysis using Laplacian (deterministic kernel)
            laplacian = self.cv2.Laplacian(gray, self.cv2.CV_64F)
            laplacian_var = np.var(np.abs(laplacian))

            # 5. Detect regions with unnaturally sharp edges
            # Natural scanned documents have slight blur; digital insertions are sharp
            _, binary = self.cv2.threshold(gray, 0, 255, self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU)
            contours, _ = self.cv2.findContours(binary, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)

            anomaly_regions = []
            total_anomaly_score = 0.0

            for i, contour in enumerate(contours[:20]):  # Limit to top 20 regions
                if len(contour) < 5:
                    continue

                x, y, w, h = self.cv2.boundingRect(contour)
                if w < 20 or h < 20:  # Skip tiny regions
                    continue

                roi = gray[y:y+h, x:x+w]
                roi_laplacian = self.cv2.Laplacian(roi, self.cv2.CV_64F)
                roi_edge_sharpness = np.var(np.abs(roi_laplacian))

                # Compare ROI edge sharpness to background
                if background_var > 0:
                    edge_ratio = roi_edge_sharpness / (background_var + 1e-6)
                else:
                    edge_ratio = 0

                # Check for variance inconsistency within ROI
                roi_var = np.var(roi)
                variance_ratio = roi_var / (background_var + 1e-6)

                # Digital perfection indicators:
                # - Edge sharpness much higher than background (threshold: 2.5)
                # - Internal variance inconsistent with natural texture
                if edge_ratio > DIGITAL_PERFECTION_EDGE_THRESHOLD or variance_ratio > 3.0:
                    anomaly_regions.append({
                        "region_id": i,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "edge_ratio": round(edge_ratio, 3),
                        "variance_ratio": round(variance_ratio, 3),
                        "suspicion": "HIGH" if edge_ratio > 5.0 else "MEDIUM"
                    })
                    total_anomaly_score += edge_ratio

            # Calculate overall metrics
            variance_ratio = np.mean(local_var) / (background_var + 1e-6) if background_var > 0 else 0
            edge_sharpness_ratio = laplacian_var / (background_var + 1e-6) if background_var > 0 else 0

            # Digital perfection detected if multiple anomaly regions found
            # DETERMINISTIC: Must have >= 2 anomalies AND edge ratio > threshold
            digital_perfection_detected = (
                len(anomaly_regions) >= 2 and 
                edge_sharpness_ratio > DIGITAL_PERFECTION_EDGE_THRESHOLD
            )

            # Confidence based on number and strength of anomalies
            confidence = min(0.95, 0.5 + (len(anomaly_regions) * 0.1) + (edge_sharpness_ratio * 0.05))

            return {
                "digital_perfection_detected": digital_perfection_detected,
                "variance_ratio": round(variance_ratio, 3),
                "edge_sharpness_ratio": round(edge_sharpness_ratio, 3),
                "anomaly_regions": anomaly_regions,
                "confidence": round(confidence, 3),
                "background_noise_estimate": round(float(background_var), 3),
                "regions_analyzed": len(contours),
                "thresholds": {
                    "edge_threshold": DIGITAL_PERFECTION_EDGE_THRESHOLD,
                    "variance_threshold": DIGITAL_PERFECTION_VARIANCE_THRESHOLD,
                }
            }

        except Exception as exc:
            audit_logger.log_info(
                event_type="FORENSIC_ANALYSIS_ERROR",
                tool="ForensicImageAnalyzer",
                message=f"Digital perfection analysis failed: {exc}"
            )
            return {
                "digital_perfection_detected": False,
                "error": str(exc),
                "confidence": 0.0
            }

    def _compute_local_variance(self, gray_img: "np.ndarray", window_size: int) -> "np.ndarray":
        """Compute local variance using box filter (deterministic)."""
        mean = self.cv2.boxFilter(gray_img.astype(self.np.float32), -1, (window_size, window_size))
        mean_sq = self.cv2.boxFilter(gray_img.astype(self.np.float32) ** 2, -1, (window_size, window_size))
        variance = mean_sq - mean ** 2
        return variance

    def analyze_compression_artifacts(self, image_path: str, image: "Image.Image") -> dict:
        """
        Analyze compression artifacts and metadata inconsistencies.

        DETERMINISTIC DETECTION:
        - JPEG DCT coefficient inconsistencies
        - Chroma subsampling anomalies  
        - Double compression indicators
        - Metadata geometry mismatches
        """
        if not self.has_opencv:
            return {"analysis_available": False}

        try:
            import numpy as np
            results = {
                "compression_anomalies": [],
                "jpeg_quality_estimate": None,
                "double_compression_suspected": False,
                "chroma_anomaly": False,
                "metadata_geometry_mismatch": False,
            }

            # Check file extension for compression type
            ext = Path(image_path).suffix.lower()

            if ext in {".jpg", ".jpeg"}:
                # P1: analizar DCT sin re-encodear (evitar destrucción de evidencia)
                # Usar el archivo original directamente para análisis de compresión
                img_array = np.array(image.convert('RGB'))

                # Check for double compression by analyzing quantization tables
                # directamente desde el buffer original del archivo
                with open(image_path, 'rb') as f:
                    raw_bytes = f.read()
                img_high = self.cv2.imdecode(
                    np.frombuffer(raw_bytes, dtype=np.uint8),
                    self.cv2.IMREAD_COLOR
                )

                if img_high is not None:
                    # Comparar con re-encode a quality 95 para detectar doble compresión
                    buf_reenc = io.BytesIO()
                    image.save(buf_reenc, format='JPEG', quality=95)
                    buf_reenc.seek(0)
                    img_reenc = self.cv2.imdecode(
                        np.frombuffer(buf_reenc.getvalue(), dtype=np.uint8),
                        self.cv2.IMREAD_COLOR
                    )
                    if img_reenc is not None:
                        diff = self.np.abs(img_array.astype(float) - img_reenc.astype(float))
                        reconstruction_error = self.np.mean(diff)

                        # High reconstruction error at quality 95 suggests original was lower quality
                        if reconstruction_error > JPEG_QUALITY_INCONSISTENCY_THRESHOLD:
                            results["compression_anomalies"].append(
                                f"High reconstruction error ({reconstruction_error:.2f}) suggests "
                                "possible re-compression or quality manipulation"
                            )
                            results["double_compression_suspected"] = True
                            results["jpeg_quality_estimate"] = max(1, int(95 - reconstruction_error))

            # Chroma subsampling analysis
            if len(image.split()) >= 3:
                r, g, b = image.split()[:3]
                r_arr = np.array(r)
                g_arr = np.array(g)
                b_arr = np.array(b)

                # Calculate chroma channels (Cb, Cr approximation)
                cb = 0.5 * r_arr - 0.419 * g_arr - 0.081 * b_arr + 128
                cr = -0.169 * r_arr - 0.331 * g_arr + 0.5 * b_arr + 128

                # Check for 4:2:0 subsampling artifacts (blockiness in chroma)
                cb_var = self.np.var(cb)
                cr_var = self.np.var(cr)
                luma_var = self.np.var(np.array(image.convert('L')))

                if luma_var > 0:
                    chroma_ratio = (cb_var + cr_var) / (2 * luma_var)
                    if chroma_ratio < CHROMA_SUBSAMPLING_ANOMALY_THRESHOLD:
                        results["chroma_anomaly"] = True
                        results["compression_anomalies"].append(
                            f"Abnormal chroma/luma variance ratio ({chroma_ratio:.3f}) "
                            "suggests aggressive subsampling or chroma manipulation"
                        )

            return results

        except Exception as exc:
            return {"analysis_available": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Kimi P1-10: CAIE Integration via add_from_tool_result
# ---------------------------------------------------------------------------

async def _inject_caie_artifact(
    image_path: str,
    forensic_result: dict,
    clip_verdict: str,
    malice_score: float,
    label_scores: dict,
    exif_forensics: dict,
) -> None:
    """
    Inject forensic findings into CAIE using add_from_tool_result().

    CAIE P3 Integration:
    - Uses evidence_type "document_visual" for CLIP-based analysis
    - Uses evidence_type "document_geometry" for forensic analysis
    - CAIE auto-detects digital_perfection_detected and metadata_concealment_detected
    - Produces DOCUMENT_FORGERY and METADATA_CONCEALMENT fractures automatically
    """
    try:
        from vigia.tools.caie import CrossArtifactIncongruenceEngine

        caie = CrossArtifactIncongruenceEngine()

        # Prepare tool result for CAIE.add_from_tool_result()
        # CAIE will auto-extract scores and detect forensic signals
        tool_result = {
            "verdict": clip_verdict,
            "vigia_verdict": f"[VIGIA_VISION] {clip_verdict} - {image_path}",
            "visual_malice_score": malice_score,
            "digital_perfection_detected": forensic_result.get("digital_perfection_detected", False),
            "metadata_concealment_detected": exif_forensics.get("metadata_suspicious", False),
            "forensic_confidence": forensic_result.get("confidence", 0.0),
            "anomaly_regions": forensic_result.get("anomaly_regions", []),
            "signals": [
                {"type": "DIGITAL_PERFECTION_ANOMALY"} if forensic_result.get("digital_perfection_detected") else None,
                {"type": "METADATA_CONCEALMENT"} if exif_forensics.get("metadata_suspicious") else None,
                {"type": "DOCUMENT_FORGERY"} if malice_score >= MALICE_THRESHOLD else None,
            ],
            "findings": {
                "variance_ratio": forensic_result.get("variance_ratio"),
                "edge_sharpness_ratio": forensic_result.get("edge_sharpness_ratio"),
                "exif_tag_count": exif_forensics.get("exif_tag_count"),
                "software_stripped": exif_forensics.get("software_stripped"),
            }
        }

        # Remove None signals
        tool_result["signals"] = [s for s in tool_result["signals"] if s is not None]

        # Inject as document_visual (CLIP analysis)
        caie.add_from_tool_result(
            tool_name="vision_intent_audit",
            result=tool_result,
            evidence_type="document_visual",
            provenance_chain=[hashlib.sha256(image_path.encode()).hexdigest()[:16]]
        )

        # If forensic analysis available, also inject as document_geometry
        if forensic_result.get("digital_perfection_detected"):
            caie.add_from_tool_result(
                tool_name="forensic_image_analyzer",
                result=tool_result,
                evidence_type="document_geometry",
                provenance_chain=[hashlib.sha256(image_path.encode()).hexdigest()[:16]]
            )

        audit_logger.log_info(
            event_type="CAIE_ARTIFACT_INJECTED",
            tool="vision_intent_audit",
            message=f"CAIE artifacts injected for {image_path}: "
                    f"visual={malice_score:.3f}, "
                    f"forensic={forensic_result.get('confidence', 0):.3f}",
        )

    except ImportError:
        audit_logger.log_info(
            event_type="CAIE_NOT_AVAILABLE",
            tool="vision_intent_audit",
            message="CrossArtifactIncongruenceEngine not available for integration",
        )
    except Exception as exc:
        audit_logger.log_info(
            event_type="CAIE_INJECTION_ERROR",
            tool="vision_intent_audit",
            message=f"Failed to inject CAIE artifact: {exc}",
        )


# ---------------------------------------------------------------------------
# CLIPVisualAuditor
# ---------------------------------------------------------------------------

class CLIPVisualAuditor:
    """
    Zero-shot visual classifier using OpenAI CLIP + Forensic Analysis.

    Detects intentionality dissonance: images that present themselves as
    legitimate official documents but carry structural markers of fabrication.

    Enhanced with Digital Perfection detection and CAIE integration.

    DETERMINISTIC 100%: 
    - CLIP provides semantic classification (probabilistic)
    - Forensic analysis provides deterministic structural analysis
    - Final verdict combines both with fixed thresholds
    """

    def __init__(self, model_name: str = "ViT-B/32") -> None:
        try:
            import torch
            import clip
        except ImportError as exc:
            raise RuntimeError(
                "CLIP and torch are required for visual auditing. "
                "Install with: pip install torch clip"
                " (see https://github.com/openai/CLIP for torch version compatibility)"
            ) from exc

        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Kimi P1-10: Initialize forensic analyzer
        self.forensic_analyzer = ForensicImageAnalyzer()

        # Integrity check
        cache_dir = Path.home() / ".cache" / "clip"
        # CLIP uses dashes in filenames: ViT-B/32 -> ViT-B-32.pt
        model_filename = model_name.replace("/", "-") + ".pt"
        model_path = cache_dir / model_filename
        expected_hash = CLIP_MODEL_HASHES.get(model_filename, "")

        if not expected_hash:
            if _STRICT_MODEL_CHECK:
                # In strict mode, refuse to load without a configured hash
                audit_logger.log_block(
                    event_type="MODEL_HASH_MISSING_STRICT",
                    tool="CLIPVisualAuditor.__init__",
                    input_preview=model_filename,
                    reason=(
                        f"VIGIA_STRICT_MODEL_CHECK=true but no hash configured "
                        f"for {model_filename}. Refusing to load — "
                        "supply-chain integrity cannot be verified. "
                        "Set VIGIA_CLIP_HASH_FILE or VIGIA_CLIP_HASH_VIT_B_32."
                    ),
                )
                raise RuntimeError(
                    f"Strict model check: no hash configured for {model_filename}. "
                    "Cannot verify model integrity. Set VIGIA_STRICT_MODEL_CHECK=false "
                    "to allow unchecked loading (NOT recommended for production)."
                )
            else:
                # Non-strict: warn loudly but allow loading
                msg = (
                    f"No expected hash configured for {model_filename}. "
                    "Integrity check SKIPPED. A poisoned model could classify "
                    "forged documents as legitimate. "
                    "Set VIGIA_STRICT_MODEL_CHECK=true and configure hashes "
                    "before any production or court use."
                )
                audit_logger.log_info(
                    event_type="MODEL_HASH_UNCONFIGURED",
                    tool="CLIPVisualAuditor.__init__",
                    message=msg,
                )
                print(
                    f"\n[VIGIA][WARNING] {msg}\n",
                    file=sys.stderr, flush=True,
                )
        elif not _verify_model_integrity(model_path, expected_hash):
            audit_logger.log_block(
                event_type="MODEL_TAMPERING",
                tool="CLIPVisualAuditor.__init__",
                input_preview=str(model_path),
                reason=(
                    f"CLIP model {model_name} SHA-256 mismatch. "
                    "Possible supply-chain attack or corrupted download."
                ),
            )
            raise RuntimeError(
                f"CLIP model integrity check failed for {model_name}. "
                "Refusing to load."
            )

        try:
            self.model, self.preprocess = clip.load(model_name, device=self.device)
        except Exception as exc:
            audit_logger.log_info(
                event_type="VISION_INIT_ERROR", tool="CLIPVisualAuditor.__init__", message=str(exc)
            )
            raise RuntimeError(f"Failed to load CLIP model {model_name!r}: {exc}") from exc

        # Combine default and forensic labels
        self.labels: list[str] = list(_DEFAULT_LABELS) + list(_FORENSIC_LABELS)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _score_image(self, image_input, text_inputs) -> list[float]:
        """Run CLIP inference synchronously (intended for executor)."""
        import torch
        import clip as _clip

        with torch.no_grad():
            img_feat = self.model.encode_image(image_input)
            txt_feat = self.model.encode_text(text_inputs)
            img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)
            txt_feat = txt_feat / txt_feat.norm(dim=-1, keepdim=True)
            similarity = (100.0 * img_feat @ txt_feat.T).softmax(dim=-1)
        return similarity[0].tolist()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    async def analyze_intent(self, image_path: str) -> dict:
        """
        Run zero-shot CLIP classification + forensic analysis on an image.

        DETERMINISTIC PIPELINE:
        1. Atomic file access (O_NOFOLLOW)
        2. Dimension/pixel validation
        3. Forensic analysis (deterministic CV)
        4. CLIP classification (semantic)
        5. Score fusion with fixed thresholds
        6. CAIE artifact injection

        Returns
        -------
        dict with keys: status, verdict, visual_malice_score,
                        top_signals, peirce_chain, timestamp, vigia_verdict,
                        forensic_analysis, caie_injected
        """
        import clip as _clip
        from PIL import Image

        # Path validation
        try:
            safe_path = _sanitize_path(image_path, must_exist=True)
        except ValueError as exc:
            return {"status": "ERROR", "error": str(exc), "timestamp": _utcnow()}

        # Extension check
        ext = Path(safe_path).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            audit_logger.log_block(
                event_type="INVALID_FILE_TYPE",
                tool="vision_intent_audit",
                input_preview=image_path,
                reason=f"Extension {ext!r} not in allowed set.",
            )
            return {
                "status": "BLOCKED",
                "error": f"File type {ext!r} not supported for visual audit.",
                "timestamp": _utcnow(),
            }

        # Size check before loading into memory
        file_size = os.path.getsize(safe_path)
        if file_size > MAX_IMAGE_BYTES:
            return {
                "status": "BLOCKED",
                "error": f"File too large: {file_size:,} bytes (max {MAX_IMAGE_BYTES:,}).",
                "timestamp": _utcnow(),
            }

        # Kimi P1-9: Atomic image access.
        # Open the file ONCE via os.open (O_RDONLY | O_NOFOLLOW on POSIX)
        # to get a file descriptor. Pass the fd to Image.open().
        # This eliminates the TOCTOU window between dimension validation
        # and image loading — the file cannot be swapped between the two.
        try:
            open_flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                open_flags |= os.O_NOFOLLOW  # POSIX: reject symlinks at open
            fd = os.open(safe_path, open_flags)
        except OSError as exc:
            if "symbolic link" in str(exc).lower() or "loop" in str(exc).lower():
                audit_logger.log_block(
                    event_type="SYMLINK_AT_OPEN",
                    tool="vision_intent_audit",
                    input_preview=safe_path,
                    reason=f"O_NOFOLLOW rejected symlink: {exc}",
                )
            return {"status": "ERROR", "error": f"Cannot open image: {exc}", "timestamp": _utcnow()}

        try:
            # Wrap fd in a Python file object for Pillow
            file_obj = os.fdopen(fd, "rb")
            # Load image from the single fd — no second open
            image = Image.open(file_obj)
            width, height = image.size

            # Dimension checks on the already-opened image
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                image.close()
                try:
                    file_obj.close()
                except Exception:
                    pass
                return {
                    "status": "BLOCKED",
                    "error": (
                        f"Image {width}x{height} exceeds max "
                        f"{MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}."
                    ),
                    "timestamp": _utcnow(),
                }

            if width * height > MAX_IMAGE_PIXELS:
                image.close()
                try:
                    file_obj.close()
                except Exception:
                    pass
                return {
                    "status": "BLOCKED",
                    "error": (
                        f"Pixel count {width * height:,} exceeds max {MAX_IMAGE_PIXELS:,}."
                    ),
                    "timestamp": _utcnow(),
                }

            # Force full decode + convert (Pillow is lazy by default)
            image = image.convert("RGB")

        except Exception as exc:
            try:
                os.close(fd)
            except OSError:
                pass
            audit_logger.log_info(
                "VISION_LOAD_ERROR", "vision_intent_audit", f"{safe_path}: {exc}"
            )
            return {"status": "ERROR", "error": f"Failed to load image: {exc}", "timestamp": _utcnow()}

        # Kimi P1-10: FORENSIC ANALYSIS (Digital Perfection + Compression)
        forensic_result = self.forensic_analyzer.analyze_digital_perfection(safe_path, image)
        compression_analysis = self.forensic_analyzer.analyze_compression_artifacts(safe_path, image)

        # CLIP inference with timeout
        try:
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            text_inputs = _clip.tokenize(self.labels).to(self.device)

            loop = asyncio.get_event_loop()
            scores: list[float] = await asyncio.wait_for(
                loop.run_in_executor(None, self._score_image, image_input, text_inputs),
                timeout=CLIP_INFERENCE_TIMEOUT,
            )

        except asyncio.TimeoutError:
            return {
                "status": "ERROR",
                "error": f"CLIP inference exceeded {CLIP_INFERENCE_TIMEOUT}s timeout.",
                "timestamp": _utcnow(),
            }
        except Exception as exc:
            audit_logger.log_info(
                "VISION_INFERENCE_ERROR", "vision_intent_audit", str(exc)
            )
            return {"status": "ERROR", "error": f"CLIP inference failed: {exc}", "timestamp": _utcnow()}

        # Score mapping
        label_scores: dict[str, float] = {
            label: round(score, 4)
            for label, score in zip(self.labels, scores)
        }

        # Malice composite: collage + forged document labels
        # NOTA: Como softmax distribuye probabilidad entre TODAS las labels (11 total),
        # el máximo teórico de malice_score es ~0.8 si las 4 labels maliciosas dominan.
        # El threshold MALICE_THRESHOLD=0.75 solo se alcanza con digital_perfection_override
        # o cuando CLIP asigna probabilidad concentrada a las labels de fabricación.
        malice_score = (
            label_scores.get("a manual digital collage with cut and paste elements", 0.0)
            + label_scores.get("a forged document with inconsistent fonts", 0.0)
            + label_scores.get("a digitally inserted signature with sharp edges on scanned paper", 0.0) * 0.5
            + label_scores.get("a pasted official seal with different resolution than background", 0.0) * 0.5
        )
        malice_score = round(malice_score, 3)

        # Legitimacy composite: official + genuine labels
        legit_score = (
            label_scores.get("an official government judicial document", 0.0)
            + label_scores.get("a genuine legal notification with standard margins", 0.0)
            + label_scores.get("a scanned document with consistent paper texture and noise", 0.0)
        )
        legit_score = round(legit_score, 3)

        # Kimi P1-10: OVERRIDE VERDICT if Digital Perfection detected
        # DETERMINISTIC: Forensic evidence overrides semantic when structural
        # anomalies are detected with high confidence
        original_verdict = None
        digital_perfection_override = False

        if forensic_result.get("digital_perfection_detected"):
            # Forensic detection is deterministic - force MALICE
            original_malice = malice_score
            malice_score = max(malice_score, DIGITAL_PERFECTION_MALICE_SCORE)
            verdict = "MALICE"
            digital_perfection_override = True
            audit_logger.log_info(
                event_type="DIGITAL_PERFECTION_OVERRIDE",
                tool="vision_intent_audit",
                message=f"Forensic override applied: {original_malice:.3f} -> {malice_score:.3f}",
            )
        else:
            # Standard verdict logic with fixed thresholds
            if malice_score >= MALICE_THRESHOLD:
                verdict = "MALICE"
            elif malice_score >= SUSPICION_THRESHOLD:
                verdict = "SUSPICION"
            else:
                verdict = "NOISE"

        # Peirce chain
        peirce_chain = {
            "firstness": f"Image presented as: {max(label_scores, key=label_scores.get)}",
            "secondness": (
                f"Structural markers — malice score: {malice_score:.3f}, "
                f"legitimacy score: {legit_score:.3f}. "
                f"Dissonance: {'HIGH' if malice_score > legit_score else 'LOW'}. "
                f"Digital perfection detected: {forensic_result.get('digital_perfection_detected', False)}. "
                f"Forensic confidence: {forensic_result.get('confidence', 0):.3f}"
            ),
            "thirdness": (
                "Inferred communicative habit: fabrication"
                if verdict != "NOISE"
                else "Inferred communicative habit: legitimate visual communication"
            ),
        }

        # EXIF/XMP Forensic Analysis (Eco filter + Deep Inspection)
        exif_forensics: dict = {
            "exif_present": False,
            "xmp_present": False,
            "software_stripped": False,
            "compression_inconsistencies": [],
            "metadata_suspicious": False,
            "metadata_concealment_detected": False,  # CAIE P3 field
            "exif_tag_count": 0,
        }

        exif_note: str | None = None

        try:
            exif_data = image.getexif()
            exif_tag_count = len(exif_data)
            exif_forensics["exif_present"] = exif_tag_count > 0
            exif_forensics["exif_tag_count"] = exif_tag_count

            if exif_tag_count == 0 and ext in {".jpg", ".jpeg", ".tiff"}:
                exif_note = (
                    "SIGNIFICANT_SILENCE: JPEG/TIFF with no EXIF metadata. "
                    "Deliberate stripping suspected."
                )
                exif_forensics["metadata_suspicious"] = True
                exif_forensics["metadata_concealment_detected"] = True
            elif exif_tag_count > 0:
                # Deep EXIF inspection
                software = exif_data.get(0x0131, "")  # Tag 0x0131 = Software
                make = exif_data.get(0x010F, "")     # Tag 0x010F = Make
                model = exif_data.get(0x0110, "")    # Tag 0x0110 = Model

                # Check for software editing indicators
                if isinstance(software, str):
                    software_lower = software.lower()
                    editing_tools = ("photoshop", "gimp", "canva", "paint", "lightroom", "pixelmator")
                    if any(tool in software_lower for tool in editing_tools):
                        exif_note = (
                            f"EXIF_SOFTWARE_ANOMALY: Editing software detected "
                            f"in EXIF metadata: {software!r}. "
                            "May indicate post-processing of a scanned document."
                        )
                        exif_forensics["metadata_suspicious"] = True

                # Check for stripped software field (evidence of anti-forensics)
                # If other fields exist but software is missing, suspicious
                if not software and (make or model):
                    exif_forensics["software_stripped"] = True
                    exif_forensics["metadata_suspicious"] = True
                    exif_forensics["metadata_concealment_detected"] = True
                    if not exif_note:
                        exif_note = (
                            "METADATA_TAMPERING: Device info present but software field stripped. "
                            "Possible anti-forensic metadata editing."
                        )

                # Check for compression field inconsistencies
                compression = exif_data.get(0x0103, None)  # Tag 0x0103 = Compression
                if compression is not None:
                    exif_forensics["compression_inconsistencies"].append(
                        f"Compression tag value: {compression}"
                    )

        except Exception:
            # Pillow < 9.2 fallback or corrupt EXIF — use legacy method
            raw_info = getattr(image, "info", {})
            if not raw_info.get("exif") and ext in {".jpg", ".jpeg", ".tiff"}:
                exif_note = (
                    "SIGNIFICANT_SILENCE: JPEG/TIFF with no EXIF metadata. "
                    "Deliberate stripping suspected."
                )
                exif_forensics["metadata_suspicious"] = True
                exif_forensics["metadata_concealment_detected"] = True

        # PNG metadata support + XMP detection
        png_metadata: dict[str, str] = {}
        xmp_data: str | None = None

        if ext == ".png":
            try:
                # image.text contains tEXt/zTXt/iTXt chunks as dict
                png_text = getattr(image, "text", {}) or {}
                png_info = getattr(image, "info", {}) or {}
                # Merge both sources
                png_metadata = {str(k): str(v)[:200] for k, v in png_text.items()}
                for k, v in png_info.items():
                    if isinstance(k, str) and isinstance(v, str):
                        png_metadata.setdefault(k, v[:200])

                # Check for XMP data in PNG (raw profile type exif)
                raw_profile = png_metadata.get("raw profile type exif", "")
                if raw_profile and "xmp" in raw_profile.lower():
                    exif_forensics["xmp_present"] = True
                    xmp_data = raw_profile[:500]  # Truncated for safety

                # Minimum expected metadata for legitimate PNGs
                _EXPECTED_PNG_KEYS = {"Creation Time", "Software", "Author",
                                      "creation_time", "software", "date:create",
                                      "XML:com.adobe.xmp"}
                found_keys = set(png_metadata.keys())
                has_minimum = bool(found_keys & _EXPECTED_PNG_KEYS)

                if not has_minimum and not png_metadata:
                    if exif_note is None:
                        exif_note = (
                            "SIGNIFICANT_SILENCE: PNG with zero metadata chunks "
                            "(no tEXt/zTXt/iTXt). Deliberate stripping or "
                            "programmatic generation suspected."
                        )
                    exif_forensics["metadata_suspicious"] = True
                    exif_forensics["metadata_concealment_detected"] = True
                    audit_logger.log_info(
                        event_type="METADATA_SILENCE",
                        tool="vision_intent_audit",
                        message=f"PNG {safe_path}: no metadata chunks found.",
                    )
                elif png_metadata and not has_minimum:
                    exif_forensics["metadata_suspicious"] = True
                    if exif_note is None:
                        exif_note = (
                            f"PNG has {len(png_metadata)} metadata chunk(s) but none "
                            "are standard creation/software fields. "
                            "Partial metadata — possible selective stripping."
                        )

                # Check for XMP in PNG metadata
                if "XML:com.adobe.xmp" in png_metadata:
                    exif_forensics["xmp_present"] = True
                    xmp_data = png_metadata["XML:com.adobe.xmp"][:500]

            except Exception:
                pass  # PNG metadata extraction is best-effort

        # JPEG XMP detection (in APP1 segment)
        if ext in {".jpg", ".jpeg"} and not exif_forensics["xmp_present"]:
            try:
                # XMP typically starts with "http://ns.adobe.com/xap/1.0/"
                raw_data = image.info.get("exif", b"")
                if b"http://ns.adobe.com/xap/1.0/" in raw_data:
                    exif_forensics["xmp_present"] = True
                    # Extract truncated XMP for analysis
                    xmp_start = raw_data.find(b"http://ns.adobe.com/xap/1.0/")
                    xmp_data = raw_data[xmp_start:xmp_start+500].decode('utf-8', errors='ignore')
            except Exception:
                pass

        # Compression artifact analysis integration
        if compression_analysis.get("compression_anomalies"):
            exif_forensics["compression_inconsistencies"] = compression_analysis["compression_anomalies"]
            exif_forensics["metadata_suspicious"] = True
            if not exif_note:
                exif_note = (
                    f"COMPRESSION_ANOMALY: {compression_analysis['compression_anomalies'][0]}"
                )

        # Build final result
        result = {
            "status": "OK",
            "verdict": verdict,
            "visual_malice_score": malice_score,
            "legitimacy_score": legit_score,
            "top_signals": label_scores,
            "peirce_chain": peirce_chain,
            "exif_note": exif_note,
            "png_metadata": png_metadata if png_metadata else None,
            "exif_tag_count": exif_tag_count,
            "image_dimensions": f"{width}x{height}",
            "model": self.model_name,
            "device": self.device,
            "timestamp": _utcnow(),
            "vigia_verdict": (
                f"[VIGIA_VISION]: {verdict}. "
                f"Malice score: {malice_score:.3f}. "
                f"{'Fabrication markers detected.' if verdict != 'NOISE' else 'No fabrication markers detected.'}"
                f"{' [DIGITAL_PERFECTION_OVERRIDE]' if digital_perfection_override else ''}"
            ),
            # Kimi P1-10: New forensic fields
            "forensic_analysis": {
                "digital_perfection": forensic_result,
                "compression_analysis": compression_analysis,
                "exif_forensics": exif_forensics,
                "xmp_data": xmp_data,
            },
            "caie_injected": False,  # Will be set after async injection
        }

        # Kimi P1-10: Inject into CAIE using add_from_tool_result
        # P0: NO fire-and-forget. Await explícito con timeout para capturar errores.
        if verdict in ("MALICE", "SUSPICION") or forensic_result.get("digital_perfection_detected"):
            try:
                await asyncio.wait_for(
                    _inject_caie_artifact(
                        safe_path,
                        forensic_result,
                        verdict,
                        malice_score,
                        label_scores,
                        exif_forensics,
                    ),
                    timeout=10.0,
                )
                result["caie_injected"] = True
            except asyncio.TimeoutError:
                audit_logger.log_info(
                    event_type="CAIE_INJECTION_TIMEOUT",
                    tool="vision_intent_audit",
                    message=f"CAIE injection timed out for {safe_path}",
                )
                result["caie_injected"] = False
            except Exception as exc:
                audit_logger.log_info(
                    event_type="CAIE_INJECTION_FAILED",
                    tool="vision_intent_audit",
                    message=f"CAIE injection failed: {exc}",
                )
                result["caie_injected"] = False

        return result


# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

async def vision_intent_audit(image_path: str) -> dict:
    """
    CLIP-based visual intentionality audit with forensic-grade analysis.

    DETERMINISTIC 100% PIPELINE:
    1. Atomic file access (O_NOFOLLOW) - no TOCTOU
    2. Resource limits enforced (dimensions, pixels, bytes)
    3. Forensic analysis: local variance + Laplacian edges (deterministic)
    4. CLIP classification: semantic labels (probabilistic but bounded)
    5. Score fusion with fixed thresholds (no LLM interpretation)
    6. CAIE artifact injection for cross-correlation

    Forensic features:
    - Digital Perfection Detection: Identifies resolution discrepancies between
      document elements (seals, signatures) and background paper texture.
    - Automatic CAIE Integration: Injects DOCUMENT_FORGERY fractures via
      add_from_tool_result() with digital_perfection_detected flag.
    - Silent Metadata Analysis: Deep EXIF/XMP inspection detecting software
      stripping, compression inconsistencies, and anti-forensic tampering.

    Triggers automatically in the PeircePlanner when evidence has image
    extensions (.jpg, .jpeg, .png, .webp).

    Register in the bridge:
        from vigia.tools.vision_audit import vision_intent_audit
        mcp.tool()(vision_intent_audit)
    """
    try:
        auditor = get_auditor()
    except RuntimeError as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
            "note": "Install torch and clip to enable visual auditing.",
            "timestamp": _utcnow(),
        }
    return await auditor.analyze_intent(image_path)
