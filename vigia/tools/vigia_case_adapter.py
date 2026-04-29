#!/usr/bin/env python3
"""
vigia/tools/vigia_case_adapter.py  v3

Convierte artefactos forenses VIGÍA → SignalOutput.
Usa SemioticDetectorV2 para analizar texto — sin heurísticas de capa Peirce.
Sin patrones → z_score bajo (benigno). Con patrones → z_score alto (malicioso).
"""
import json, sys, os
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for p in [_ROOT, os.path.join(_ROOT,"vigia","core")]:
    if p not in sys.path:
        sys.path.insert(0, p)

PEIRCE_Z = {"THIRDNESS": 3.2, "SECONDNESS": 2.4, "FIRSTNESS": 1.7}

TYPE_TOOL = {
    "registry":"REG","network_flow":"NET","bash_history":"CLI",
    "file_system":"FS","process":"PROC","memory":"MEM","log":"LOG",
    "auth_log":"LOG","email":"EML","browser":"BRW","usb":"USB",
    "prefetch":"PFT","lnk":"LNK","scheduled_task":"SCHED",
    "service":"SVC","user_account":"USR","crypto":"CRY",
    "timeline":"TML","artifact":"ART","file_metadata":"FS",
}

def _load_detector():
    try:
        from semiotic_detector_v2 import SemioticDetectorV2
        d = SemioticDetectorV2()
        return d
    except Exception:
        return None

_DETECTOR = _load_detector()

def artifact_to_signal(artifact: dict) -> dict:
    layer     = artifact.get("peirce_layer", "SECONDNESS").upper()
    art_type  = artifact.get("type", "unknown")
    anomalies = artifact.get("forensic_anomalies", [])
    content   = artifact.get("content", "")
    art_id    = artifact.get("artifact_id", "ART-000")
    tool_name = TYPE_TOOL.get(art_type, art_type.upper()[:6])
    z_base    = PEIRCE_Z.get(layer, 2.0)

    text = " | ".join(anomalies)
    if content:
        text = text + " | " + content[:300]

    if _DETECTOR and text.strip():
        try:
            result    = _DETECTOR.analyze(text, art_id, "2026-01-01T00:00:00Z")
            alert     = result.get("alert_level", "NORMAL")
            mi        = result.get("fsv", {}).get("manipulation_index", {})
            mi_val    = mi.get("num", 0) / max(mi.get("den", 1), 1)
            n_matches = len(result.get("matches", []))

            if n_matches == 0 and alert == "NORMAL":
                # Sin patrones semióticos = probablemente benigno
                value, z_score, confidence = 0.1, 0.4, 0.6
            else:
                boost_map = {"CRITICAL":1.2,"HIGH":1.0,"MEDIUM":0.7,
                             "LOW":0.3,"NORMAL":0.2}
                boost     = boost_map.get(alert, 0.2)
                value     = round(min(0.95, max(0.05, mi_val * boost + 0.05)), 3)
                z_score   = round(z_base * boost if boost > 0.5 else z_base * 0.4, 3)
                confidence = 0.92 if alert in ("CRITICAL","HIGH") else 0.75
        except Exception:
            n = len(anomalies)
            value     = round(min(0.7, max(0.1, 0.1 + n * 0.15)), 3)
            z_score   = round(z_base * 0.6, 3)
            confidence = 0.65
    else:
        n = len(anomalies)
        value     = round(min(0.7, max(0.1, 0.1 + n * 0.15)), 3)
        z_score   = round(z_base * 0.6, 3)
        confidence = 0.65

    return {
        "tool_name":  tool_name,
        "value":      value,
        "z_score":    z_score,
        "confidence": confidence,
        "metadata": {
            "artifact_id":  art_id,
            "peirce_layer": layer,
            "type":         art_type,
            "anomalies":    anomalies[:2],
        }
    }

def convert_case(case_path: str) -> list:
    with open(case_path) as f:
        case = json.load(f)
    artifacts = case.get("artifacts", [])
    signals   = [artifact_to_signal(a) for a in artifacts]
    print(f"Caso: {Path(case_path).stem}", file=sys.stderr)
    print(f"  Veredicto esperado: {case.get('expected_verdict','?')}", file=sys.stderr)
    print(f"  Detector: {'SemioticDetectorV2' if _DETECTOR else 'fallback'}", file=sys.stderr)
    print(f"  Señales: {len(signals)}", file=sys.stderr)
    return signals

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 vigia_case_adapter.py <caso.json> [output.json]")
        sys.exit(1)
    signals = convert_case(sys.argv[1])
    output  = json.dumps(signals, indent=2, ensure_ascii=False)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            f.write(output)
        print(f"Guardado en {sys.argv[2]}", file=sys.stderr)
    else:
        print(output)
