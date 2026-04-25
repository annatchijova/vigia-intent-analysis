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
# vigia/report/report_exporter_v2.py

import hashlib
import json
import datetime
from io import BytesIO
from typing import Dict, Any, Optional

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    PageBreak, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

import base64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_base64_image(b64: str) -> BytesIO:
    return BytesIO(base64.b64decode(b64))


def utc_now() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# ---------------------------------------------------------------------------
# Firma digital (simple, extensible)
# ---------------------------------------------------------------------------

def sign_hash(hash_hex: str, private_key=None) -> Optional[str]:
    """
    Firma el hash si se provee clave privada.
    Placeholder: integrar con cryptography o HSM.
    """
    if private_key is None:
        return None

    # Ejemplo conceptual (NO producción)
    return f"SIGNED({hash_hex[:16]})"


# ---------------------------------------------------------------------------
# Cadena de custodia
# ---------------------------------------------------------------------------

def build_chain_of_custody(report: Dict[str, Any]) -> list:
    return [
        {
            "event": "INGESTION",
            "timestamp": report["case"].get("analysis_timestamp"),
            "actor": "VIGIA_PIPELINE",
        },
        {
            "event": "SIGNAL_EXTRACTION",
            "timestamp": utc_now(),
            "actor": "signal_adapter",
        },
        {
            "event": "LIKELIHOOD_INFERENCE",
            "timestamp": utc_now(),
            "actor": "calibrated_engine",
        },
        {
            "event": "REPORT_GENERATION",
            "timestamp": utc_now(),
            "actor": "report_builder",
        },
    ]


# ---------------------------------------------------------------------------
# Exportador principal
# ---------------------------------------------------------------------------

def export_pdf(
    report: Dict[str, Any],
    output_path: str,
    private_key=None,
) -> Dict[str, Any]:
    """
    Genera PDF forense con anexos, hash y firma.
    Retorna metadata verificable.
    """

    styles = getSampleStyleSheet()
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # -----------------------------------------------------------------------
    # PORTADA
    # -----------------------------------------------------------------------

    elements.append(Paragraph("INFORME PERICIAL FORENSE", styles["Title"]))
    elements.append(Spacer(1, 12))

    case = report["case"]
    elements.append(Paragraph(f"Documento ID: {case['document_id']}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha: {case['analysis_timestamp']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # RESULTADO
    # -----------------------------------------------------------------------

    fr = report["forensic_result"]

    elements.append(Paragraph("Resultado Forense", styles["Heading2"]))
    elements.append(Paragraph(f"LR: {fr['likelihood_ratio']}", styles["Normal"]))
    elements.append(Paragraph(f"Posterior: {fr['posterior_probability']}", styles["Normal"]))
    elements.append(Paragraph(f"ENFSI: {fr['enfsi_label']}", styles["Normal"]))
    elements.append(Paragraph(fr["narrative"], styles["Normal"]))
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # MÉTRICAS
    # -----------------------------------------------------------------------

    mp = report["model_performance"]

    elements.append(Paragraph("Validación del Modelo", styles["Heading2"]))
    elements.append(Paragraph(f"AUC: {mp['auc']}", styles["Normal"]))
    elements.append(Paragraph(f"Brier Score: {mp['brier_score']}", styles["Normal"]))
    elements.append(Paragraph(f"ECE: {mp['expected_calibration_error']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # GRÁFICOS
    # -----------------------------------------------------------------------

    plots = report.get("plots", {})

    if plots.get("roc_curve"):
        elements.append(Paragraph("ROC Curve", styles["Heading3"]))
        elements.append(Image(decode_base64_image(plots["roc_curve"]), width=400, height=250))

    if plots.get("calibration_curve"):
        elements.append(Paragraph("Calibration Curve", styles["Heading3"]))
        elements.append(Image(decode_base64_image(plots["calibration_curve"]), width=400, height=250))

    elements.append(PageBreak())

    # -----------------------------------------------------------------------
    # SEÑALES
    # -----------------------------------------------------------------------

    elements.append(Paragraph("Señales Analizadas", styles["Heading2"]))

    table_data = [["Tool", "Z", "Confidence"]]
    for s in report["signals"]:
        table_data.append([s["tool"], s["z_score"], s["confidence"]])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # TRAZABILIDAD
    # -----------------------------------------------------------------------

    mt = report["model_traceability"]

    elements.append(Paragraph("Trazabilidad", styles["Heading2"]))
    elements.append(Paragraph(f"Dataset hash: {mt['dataset_hash']}", styles["Normal"]))
    elements.append(Paragraph(f"Calibration date: {mt['calibration_date']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------------------------
    # CADENA DE CUSTODIA
    # -----------------------------------------------------------------------

    custody = build_chain_of_custody(report)

    elements.append(Paragraph("Cadena de Custodia", styles["Heading2"]))
    for event in custody:
        elements.append(Paragraph(
            f"{event['timestamp']} — {event['event']} — {event['actor']}",
            styles["Normal"]
        ))

    elements.append(PageBreak())

    # -----------------------------------------------------------------------
    # ANEXOS TÉCNICOS
    # -----------------------------------------------------------------------

    elements.append(Paragraph("Anexo Técnico", styles["Heading2"]))

    elements.append(Paragraph(
        json.dumps(report["model_traceability"], indent=2),
        styles["Code"]
    ))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        json.dumps(report["model_performance"], indent=2),
        styles["Code"]
    ))

    elements.append(Spacer(1, 24))

    # Firmas
    elements.append(Paragraph("Firma Perito: ____________________", styles["Normal"]))
    elements.append(Paragraph("Firma Supervisor: ________________", styles["Normal"]))

    # -----------------------------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------------------------

    doc.build(elements)

    pdf_bytes = buffer.getvalue()

    # -----------------------------------------------------------------------
    # HASH + FIRMA
    # -----------------------------------------------------------------------

    pdf_hash = sha256_bytes(pdf_bytes)
    signature = sign_hash(pdf_hash, private_key)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return {
        "output_path": output_path,
        "pdf_hash": pdf_hash,
        "signature": signature,
        "generated_at": utc_now(),
    }
