# vigia/report/evidence_bundle.py

import os
import json
import hashlib
import zipfile
from typing import Dict, Any, Optional

from vigia.core.atomic_io import atomic_write_text, atomic_write_bytes


# ---------------------------------------------------------------------------
# Hash helper
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    """P1-10: usa O_NOFOLLOW para prevenir TOCTOU via symlink race."""
    import os
    h = hashlib.sha256()
    # O_NOFOLLOW rechaza symlinks — previene sustitución entre validación y apertura
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(path, flags)
    try:
        with os.fdopen(fd, "rb", closefd=False) as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    finally:
        os.close(fd)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def build_manifest(
    pdf_path: str,
    ledger_path: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    pdf_hash = sha256_file(pdf_path)
    ledger_hash = sha256_file(ledger_path)

    manifest = {
        "version": "v1.0",
        "artifacts": {
            "report_pdf": {
                "path": os.path.basename(pdf_path),
                "sha256": pdf_hash,
            },
            "ledger": {
                "path": os.path.basename(ledger_path),
                "sha256": ledger_hash,
            },
        },
        "binding": {
            "pdf_hash": pdf_hash,
            "ledger_hash": ledger_hash,
        },
        "metadata": metadata,
    }

    # Hash del manifest (clave)
    manifest_str = json.dumps(manifest, sort_keys=True)
    manifest["manifest_hash"] = hashlib.sha256(manifest_str.encode()).hexdigest()

    return manifest


# ---------------------------------------------------------------------------
# Firma (placeholder)
# ---------------------------------------------------------------------------

def sign_manifest(manifest_hash: str, private_key=None) -> Optional[str]:
    if private_key is None:
        return None
    return f"SIGNED({manifest_hash[:16]})"


# ---------------------------------------------------------------------------
# Builder principal
# ---------------------------------------------------------------------------

def build_evidence_bundle(
    pdf_path: str,
    ledger_dict: Dict[str, Any],
    output_dir: str,
    case_id: str,
    metadata: Dict[str, Any],
    private_key=None,
    zip_output: bool = True,
) -> Dict[str, Any]:
    """
    Genera bundle verificable:
    - PDF
    - ledger.json
    - manifest.json (con hashes)
    - firma opcional
    """

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Paths
    # -----------------------------------------------------------------------

    bundle_dir = os.path.join(output_dir, f"{case_id}_bundle")
    os.makedirs(bundle_dir, exist_ok=True)

    pdf_out = os.path.join(bundle_dir, "report.pdf")
    ledger_out = os.path.join(bundle_dir, "ledger.json")
    manifest_out = os.path.join(bundle_dir, "manifest.json")
    sig_out = os.path.join(bundle_dir, "bundle.sig")

    # -----------------------------------------------------------------------
    # Copiar PDF
    # -----------------------------------------------------------------------

    # B-064: escrituras atómicas (patrón L-023) — un crash a mitad de
    # escritura no puede dejar un artefacto de custodia truncado en disco.
    with open(pdf_path, "rb") as src:
        atomic_write_bytes(pdf_out, src.read())

    # -----------------------------------------------------------------------
    # Guardar ledger
    # -----------------------------------------------------------------------

    atomic_write_text(ledger_out, json.dumps(ledger_dict, indent=2))

    # -----------------------------------------------------------------------
    # Manifest
    # -----------------------------------------------------------------------

    manifest = build_manifest(pdf_out, ledger_out, metadata)

    atomic_write_text(manifest_out, json.dumps(manifest, indent=2))

    # -----------------------------------------------------------------------
    # Firma
    # -----------------------------------------------------------------------

    signature = sign_manifest(manifest["manifest_hash"], private_key)

    if signature:
        atomic_write_text(sig_out, signature)

    # -----------------------------------------------------------------------
    # ZIP opcional
    # -----------------------------------------------------------------------

    zip_path = None
    if zip_output:
        zip_path = os.path.join(output_dir, f"{case_id}_bundle.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for fname in os.listdir(bundle_dir):
                z.write(
                    os.path.join(bundle_dir, fname),
                    arcname=fname
                )

    return {
        "bundle_dir": bundle_dir,
        "zip_path": zip_path,
        "manifest_hash": manifest["manifest_hash"],
        "pdf_hash": manifest["artifacts"]["report_pdf"]["sha256"],
        "ledger_hash": manifest["artifacts"]["ledger"]["sha256"],
        "signature": signature,
    }
