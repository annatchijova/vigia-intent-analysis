#!/usr/bin/env python3
"""
convert_mans_to_ebs.py — Conversor Redline .mans → VIGÍA EBS v1 JSON

Parsea la base de datos SQLite de Redline/Mandiant (.mans) y genera
un caso JSON compatible con el schema EBS v1 para el pipeline VIGÍA.

Uso:
    python3 convert_mans_to_ebs.py <archivo.mans> [--out <output.json>]

Desarrollado durante análisis del caso VIGIA-REAL-NFURY (2026-05-29).
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_mans(db_path: str) -> dict:
    con = sqlite3.connect(db_path)

    # System info
    si = dict(zip(
        [r[1] for r in con.execute("PRAGMA table_info(SystemInformation)")],
        con.execute("SELECT * FROM SystemInformation LIMIT 1").fetchone() or []
    ))

    # MRI scores por proceso
    mri = {r[0]: r[1] for r in con.execute(
        "SELECT ProcessID, Score FROM MRIScores ORDER BY Score DESC"
    )}

    # Procesos
    procs = {}
    for r in con.execute("SELECT ID, PID, ParentPID, ProcessName, Path, Username FROM Processes"):
        procs[r[0]] = {"id": r[0], "pid": r[1], "ppid": r[2],
                       "name": r[3], "path": r[4], "user": r[5],
                       "mri": mri.get(r[0], 0)}

    # Árbol — detectar anomalías PPID
    pid_to_name = {v["pid"]: v["name"] for v in procs.values()}
    anomalies = []
    for p in procs.values():
        parent_name = pid_to_name.get(p["ppid"], f"PID_{p['ppid']}")
        if p["name"] in ("csrss.exe", "winlogon.exe", "lsass.exe"):
            if parent_name not in ("smss.exe", "wininit.exe", f"PID_{p['ppid']}"):
                anomalies.append(
                    f"PPID anomaly: {p['name']} PID={p['pid']} "
                    f"parent={parent_name} (PID={p['ppid']}) — expected smss/wininit"
                )

    # Top procesos sospechosos por MRI
    top_mri = sorted(procs.values(), key=lambda x: x["mri"], reverse=True)[:5]

    # Puertos
    port_cols = [r[1] for r in con.execute("PRAGMA table_info(Ports)")]
    ports = [dict(zip(port_cols, r)) for r in con.execute("SELECT * FROM Ports")]
    suspicious_ports = [p for p in ports if p.get("LocalPort") in (3389, 4444, 5985, 8080)]

    # Conexiones establecidas a IPs externas
    established = [
        p for p in ports
        if str(p.get("PortState", "")).upper() in ("ESTABLISHED", "CLOSE_WAIT")
        and p.get("RemoteAddress") and p.get("RemoteAddress") not in ("*", "")
    ]

    con.close()
    return {
        "sysinfo": si,
        "top_mri": top_mri,
        "anomalies": anomalies,
        "suspicious_ports": suspicious_ports,
        "established": established,
        "all_procs": list(procs.values()),
    }


def build_ebs(data: dict, mans_path: str, case_id: str) -> dict:
    si = data["sysinfo"]
    hostname = si.get("Hostname") or si.get("MachineName") or "UNKNOWN"
    domain = si.get("Domain", "")

    artifacts = []
    provenance_chain = [
        "F-Response Enterprise live acquisition",
        "Redline 2.0.4.0 .mans SQLite analysis",
        f"VIGÍA convert_mans_to_ebs v1.0"
    ]

    def make_hash(key: str) -> str:
        return "sha256:" + hashlib.sha256(key.encode()).hexdigest()

    # ART-001: Proceso de mayor MRI score
    if data["top_mri"]:
        top = data["top_mri"][0]
        art_id = f"{case_id}:ART-001"
        meta = {
            "pid": top["pid"], "ppid": top["ppid"],
            "name": top["name"], "path": top["path"],
            "mri_score": top["mri"], "process_exited": not top["path"],
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": make_hash(art_id),
            "acquisition_timestamp": "1970-01-01T00:00:00Z",  # actualizar con fecha real
            "write_blocker_used": False,
            "examiner_id": "TBD"
        }
        raw = min(0.95, top["mri"] / 100.0 + 0.3)
        artifacts.append({
            "artifact_id": "ART-001",
            "evidence_type": "memory_process",
            "source_tool": "Redline/MRI",
            "description": (
                f"{top['name']} (PID={top['pid']}) MRI score={top['mri']}. "
                f"{'No filesystem path — process may have exited.' if not top['path'] else f'Path: {top[\"path\"]}'} "
                + (" ".join(data["anomalies"]) if data["anomalies"] else "")
            ),
            "raw_score": round(raw, 2),
            "prior_trust": 0.70,
            "provenance_chain": provenance_chain,
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": meta["acquisition_hash"],
            "acquisition_timestamp": meta["acquisition_timestamp"],
            "write_blocker_used": False,
            "examiner_id": "TBD",
            "metadata": meta,
            "timestamp": "1970-01-01T00:00:00Z"
        })

    # ART-002: PPID anomalies (si existen)
    if data["anomalies"]:
        art_id = f"{case_id}:ART-002"
        meta = {
            "anomalies": data["anomalies"],
            "assessment": "requires_manual_review",
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": make_hash(art_id),
            "acquisition_timestamp": "1970-01-01T00:00:00Z",
            "write_blocker_used": False,
            "examiner_id": "TBD"
        }
        artifacts.append({
            "artifact_id": "ART-002",
            "evidence_type": "memory_process",
            "source_tool": "Redline/ProcessTree",
            "description": "Process tree PPID anomalies detected. " + " | ".join(data["anomalies"]),
            "raw_score": 0.40,
            "prior_trust": 0.60,
            "provenance_chain": provenance_chain,
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": meta["acquisition_hash"],
            "acquisition_timestamp": meta["acquisition_timestamp"],
            "write_blocker_used": False,
            "examiner_id": "TBD",
            "metadata": meta,
            "timestamp": "1970-01-01T00:00:00Z"
        })

    # ART-003: Conexiones establecidas sospechosas
    if data["established"]:
        art_id = f"{case_id}:ART-003"
        conns = [f"{c.get('PortProcessName','?')}→{c.get('RemoteAddress','?')}:{c.get('RemotePort','?')}"
                 for c in data["established"][:5]]
        meta = {
            "connections": conns,
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": make_hash(art_id),
            "acquisition_timestamp": "1970-01-01T00:00:00Z",
            "write_blocker_used": False,
            "examiner_id": "TBD"
        }
        artifacts.append({
            "artifact_id": "ART-003",
            "evidence_type": "network_flow",
            "source_tool": "Redline/Ports",
            "description": "Active network connections: " + "; ".join(conns),
            "raw_score": 0.55,
            "prior_trust": 0.70,
            "provenance_chain": provenance_chain,
            "acquisition_tool": "f-response enterprise",
            "acquisition_hash": meta["acquisition_hash"],
            "acquisition_timestamp": meta["acquisition_timestamp"],
            "write_blocker_used": False,
            "examiner_id": "TBD",
            "metadata": meta,
            "timestamp": "1970-01-01T00:00:00Z"
        })

    return {
        "case_id": case_id,
        "case_name": f"Redline Analysis — {hostname}",
        "description": f"Automated conversion from {Path(mans_path).name}. Hostname: {hostname}. Domain: {domain}. Manual review required for timestamps and acquisition dates.",
        "expected_verdict": "SUSPICION",
        "schema_version": "1.0",
        "artifacts": artifacts,
        "_converter_note": "Timestamps set to 1970-01-01 — update with actual acquisition dates from FTK .txt metadata"
    }


def main():
    parser = argparse.ArgumentParser(description="Convierte Redline .mans → VIGÍA EBS v1 JSON")
    parser.add_argument("mans", help="Ruta al archivo .mans (SQLite)")
    parser.add_argument("--out", help="Archivo JSON de salida (default: <case_id>.json)")
    parser.add_argument("--case-id", help="ID del caso (default: VIGIA-MANS-<hash>)")
    args = parser.parse_args()

    if not os.path.exists(args.mans):
        print(f"ERROR: {args.mans} no encontrado", file=sys.stderr)
        sys.exit(1)

    case_id = args.case_id or f"VIGIA-MANS-{hashlib.sha256(args.mans.encode()).hexdigest()[:8].upper()}"
    out = args.out or f"{case_id}.json"

    print(f"Parseando {args.mans}...")
    data = parse_mans(args.mans)
    print(f"  Procesos: {len(data['all_procs'])}  Anomalías PPID: {len(data['anomalies'])}  Conexiones: {len(data['established'])}")

    case = build_ebs(data, args.mans, case_id)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(case, f, indent=2, ensure_ascii=False)

    print(f"Caso guardado: {out}")
    print(f"NOTA: Actualizar acquisition_timestamp con fechas reales del .txt de FTK")


if __name__ == "__main__":
    main()
