"""
vigia/tools/vision_audit.py
===========================
VIGIA - Visual Intentionality Audit using CLIP.

Detects intentionality dissonance in images and scanned documents:
whether a visual artifact looks official but carries structural markers
of fabrication (cut-paste, digital collage, pasted seals).

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
import os
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
    "ViT-B-32.pt": "",   # TODO: populate with sha256sum output
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

# ---------------------------------------------------------------------------
# Module-level singleton (lazy)
# ---------------------------------------------------------------------------

_auditor_instance: "CLIPVisualAuditor | None" = None


def get_auditor(model_name: str = "ViT-B/32") -> "CLIPVisualAuditor":
    """
    Return the module-level CLIPVisualAuditor singleton, creating it on first
    call.  Raises RuntimeError if torch or clip are not installed.
    """
    global _auditor_instance
    if _auditor_instance is None:
        _auditor_instance = CLIPVisualAuditor(model_name=model_name)
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
# CLIPVisualAuditor
# ---------------------------------------------------------------------------

class CLIPVisualAuditor:
    """
    Zero-shot visual classifier using OpenAI CLIP.

    Detects intentionality dissonance: images that present themselves as
    legitimate official documents but carry structural markers of fabrication.
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
                "VISION_INIT_ERROR", "CLIPVisualAuditor.__init__", str(exc)
            )
            raise RuntimeError(f"Failed to load CLIP model {model_name!r}: {exc}") from exc

        self.labels: list[str] = list(_DEFAULT_LABELS)

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
        Run zero-shot CLIP classification on an image and return a VIGIA
        intent verdict.

        Returns
        -------
        dict with keys: status, verdict, visual_malice_score,
                        top_signals, peirce_chain, timestamp, vigia_verdict
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
        malice_score = (
            label_scores.get("a manual digital collage with cut and paste elements", 0.0)
            + label_scores.get("a forged document with inconsistent fonts", 0.0)
        )
        malice_score = round(malice_score, 3)

        # Legitimacy composite: official + genuine labels
        legit_score = (
            label_scores.get("an official government judicial document", 0.0)
            + label_scores.get("a genuine legal notification with standard margins", 0.0)
        )
        legit_score = round(legit_score, 3)

        # Verdict
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
                f"Dissonance: {'HIGH' if malice_score > legit_score else 'LOW'}"
            ),
            "thirdness": (
                "Inferred communicative habit: fabrication"
                if verdict != "NOISE"
                else "Inferred communicative habit: legitimate visual communication"
            ),
        }

        # EXIF silence check (Eco filter)
        # Modernized for Pillow 9.2+: use image.getexif() instead of
        # the deprecated image.info["exif"] raw bytes approach.
        # getexif() returns an IFD dict; empty dict = no EXIF data.
        exif_note: str | None = None
        exif_tag_count = 0
        try:
            exif_data = image.getexif()
            exif_tag_count = len(exif_data)
            if exif_tag_count == 0 and ext in {".jpg", ".jpeg", ".tiff"}:
                exif_note = (
                    "SIGNIFICANT_SILENCE: JPEG/TIFF with no EXIF metadata. "
                    "Deliberate stripping suspected."
                )
            elif exif_tag_count > 0:
                # Check for suspicious EXIF patterns
                # Tag 0x0131 = Software, Tag 0x010F = Make
                software = exif_data.get(0x0131, "")
                if isinstance(software, str) and any(
                    tool in software.lower()
                    for tool in ("photoshop", "gimp", "canva", "paint")
                ):
                    exif_note = (
                        f"EXIF_SOFTWARE_ANOMALY: Editing software detected "
                        f"in EXIF metadata: {software!r}. "
                        "May indicate post-processing of a scanned document."
                    )
        except Exception:
            # Pillow < 9.2 fallback or corrupt EXIF — use legacy method
            raw_info = getattr(image, "info", {})
            if not raw_info.get("exif") and ext in {".jpg", ".jpeg", ".tiff"}:
                exif_note = (
                    "SIGNIFICANT_SILENCE: JPEG/TIFF with no EXIF metadata. "
                    "Deliberate stripping suspected."
                )

        # Kimi P1-7: PNG metadata support
        # PNG files use tEXt/zTXt/iTXt chunks instead of EXIF.
        # Pillow exposes these via image.info dict and image.text attribute.
        png_metadata: dict[str, str] = {}
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

                # Minimum expected metadata for legitimate PNGs
                _EXPECTED_PNG_KEYS = {"Creation Time", "Software", "Author",
                                      "creation_time", "software", "date:create"}
                found_keys = set(png_metadata.keys())
                has_minimum = bool(found_keys & _EXPECTED_PNG_KEYS)

                if not has_minimum and not png_metadata:
                    if exif_note is None:
                        exif_note = (
                            "SIGNIFICANT_SILENCE: PNG with zero metadata chunks "
                            "(no tEXt/zTXt/iTXt). Deliberate stripping or "
                            "programmatic generation suspected."
                        )
                    audit_logger.log_info(
                        event_type="METADATA_SILENCE",
                        tool="vision_intent_audit",
                        message=f"PNG {safe_path}: no metadata chunks found.",
                    )
                elif png_metadata and not has_minimum:
                    if exif_note is None:
                        exif_note = (
                            f"PNG has {len(png_metadata)} metadata chunk(s) but none "
                            "are standard creation/software fields. "
                            "Partial metadata — possible selective stripping."
                        )
            except Exception:
                pass  # PNG metadata extraction is best-effort

        return {
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
            ),
        }


# ---------------------------------------------------------------------------
# MCP tool function
# ---------------------------------------------------------------------------

async def vision_intent_audit(image_path: str) -> dict:
    """
    CLIP-based visual intentionality audit.

    Determines whether an image (scanned document, screenshot, official seal)
    presents structural markers of digital fabrication.

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
