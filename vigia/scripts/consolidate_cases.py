#!/usr/bin/env python3
"""
vigia/pipeline/consolidate_cases.py

Consolida casos forenses de múltiples fuentes en formato canónico VIGÍA.

Fuentes soportadas:
  1. Markdown narrativo (casos sintéticos: casos.md, nuevoscasos.md, casosfinal.md, etc.)
  2. JSON estructurado (output de Kimi Agent, datasets públicos)
  3. JSON legacy (casos ya existentes en data/cases/)

Output: data/cases/consolidated/ con IDs canónicos + _index.json

Formato canónico VIGÍA v1.0:
  {
    case_id, case_name, source_origin, source_dataset,
    description, expected_verdict, confidence_expected,
    expected_mitre_ttps, carnegie_pattern_expected,
    artifacts: [{artifact_id, type, content, forensic_anomalies, peirce_layer}],
    peirce_expected: {firstness, secondness, thirdness},
    devil_advocate, abstention_risk
  }

Uso:
    python3 vigia/pipeline/consolidate_cases.py \\
        --md-sources casos.md nuevoscasos.md casosfinal.md casos2.md casoscasos.md \\
        --json-sources data/cases/ \\
        --output data/cases/consolidated/ \\
        --validate

Autor: Colectivo VIGÍA (diseño Kimi, implementación Claude)
Versión: 2.3
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Esquema canónico ─────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    "case_id", "case_name", "source_origin", "description",
    "expected_verdict", "confidence_expected", "artifacts",
    "peirce_expected", "devil_advocate",
]

VERDICTS_ALLOWED = {"MALICE", "INTENT", "SUSPICION", "NOISE", "ABSTAIN"}

ARTIFACT_TYPES = {
    "auth_log", "bash_history", "network_flow", "file_metadata",
    "registry", "process_list", "memory_string", "exif",
    "pdf_metadata", "email_header", "dns_log", "timestamp",
    "slack_message", "jira_ticket", "powershell_log", "syslog",
}

DEVIL_ADVOCATE_TEMPLATES = {
    "MALICE": "El comportamiento observado podría explicarse por un error administrativo, una configuración automatizada legítima, o un malentendido de procedimientos internos.",
    "INTENT": "Las inconsistencias detectadas podrían deberse a un cambio de hábitos personales, una rotación de personal, o una herramienta de automatización no documentada.",
    "SUSPICION": "Los artefactos presentes son ambiguos y podrían ser residuos de actividad legítima de mantenimiento o pruebas de seguridad autorizadas.",
    "NOISE": "El patrón observado es consistente con ruido de fondo del sistema, actividad de usuarios legítimos, o artefactos de software benigno.",
    "ABSTAIN": "La evidencia es insuficiente para formular una hipótesis benigna competente.",
}


# ── Canonicalizer (I7 compliant) ──────────────────────────────────────────

def _canonicalize(obj: Any) -> Any:
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return f"{obj}:int"
    if isinstance(obj, float):
        return f"{obj:.8f}"
    if isinstance(obj, dict):
        return {k: _canonicalize(v) for k, v in sorted(obj.items())}
    if isinstance(obj, (list, tuple)):
        return [_canonicalize(v) for v in obj]
    return str(obj)


def _content_hash(case: Dict[str, Any]) -> str:
    canonical = json.dumps(_canonicalize(case), sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


# ── Parser de Markdown narrativo ──────────────────────────────────────────

class MarkdownCaseParser:
    """
    Extrae casos de archivos Markdown con formato narrativo VIGÍA.
    Soporta el formato:
        Caso NNN: "Nombre" – Subtítulo
        Signals: ...
        Carnegie Appeal: ...
        Peirce: ...
        Interpretación de VIGÍA: "..." Veredicto: VERDICT (XX%)
    """

    # Patrones de cabecera de caso — tolerantes a variaciones de formato
    CASE_HEADER_PATTERNS = [
        re.compile(
            r'(?:^|\n)(?:#{1,4}\s*)?Caso\s+(\d+)[:\.\s]+[""«]?([^"\n—–\-]+)[""»]?\s*[—–\-]+\s*(.+?)(?=\n|$)',
            re.IGNORECASE
        ),
        re.compile(
            r'(?:^|\n)(?:#{1,4}\s*)?Caso\s+(\d+)[:\.\s]+(.+?)(?=\n|$)',
            re.IGNORECASE
        ),
    ]

    VERDICT_RE = re.compile(
        r'[Vv]eredicto[:\s*]*[*]*\s*(MALICE|INTENT|SUSPICION|NOISE|ABSTAIN)\s*(?:\((\d+)%?\))?',
        re.IGNORECASE
    )
    SIGNALS_RE = re.compile(r'\*?\*?Signals?[:\*]+\s*(.*?)(?=\n\s*\n|\n\s*\*?\*?(?:Carnegie|Grice|Peirce|Eco|Interpretación)|$)', re.DOTALL | re.IGNORECASE)
    CARNEGIE_RE = re.compile(r'\*?\*?Carnegie[^:\n]*[:\*]+\s*(.*?)(?=\n\s*\n|\n\s*\*?\*?(?:Grice|Peirce|Eco|Interpretación|Caso\s+\d)|$)', re.DOTALL | re.IGNORECASE)
    PEIRCE_RE = re.compile(r'\*?\*?Peirce[^:\n]*[:\*]+\s*(.*?)(?=\n\s*\n|\n\s*\*?\*?(?:Grice|Eco|Interpretación|Carnegie|Caso\s+\d)|$)', re.DOTALL | re.IGNORECASE)
    GRICE_RE = re.compile(r'\*?\*?Grice[^:\n]*[:\*]+\s*(.*?)(?=\n\s*\n|\n\s*\*?\*?(?:Peirce|Eco|Interpretación|Carnegie|Caso\s+\d)|$)', re.DOTALL | re.IGNORECASE)
    ECO_RE = re.compile(r'\*?\*?Eco[^:\n]*[:\*]+\s*(.*?)(?=\n\s*\n|\n\s*\*?\*?(?:Peirce|Grice|Interpretación|Carnegie|Caso\s+\d)|$)', re.DOTALL | re.IGNORECASE)
    INTERPRETATION_RE = re.compile(r'Interpretación\s+de\s+VIG[IÍ]A[^:]*:[:\s]*[""«]?(.+?)[""»]?(?:\s*Veredicto|$)', re.DOTALL | re.IGNORECASE)

    def parse_file(self, path: str) -> List[Dict[str, Any]]:
        import os as _os
        if _os.path.getsize(path) > 2 * 1024 * 1024:
            raise ValueError(f"[VIGIA] Markdown demasiado grande: {path}")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        cases = []
        # Dividir el texto en bloques de casos
        blocks = self._split_into_blocks(text)

        for block_num, block_name, block_subtitle, block_body in blocks:
            case = self._parse_case_body(block_num, block_name, block_subtitle, block_body)
            if case:
                cases.append(case)

        return cases

    def _split_into_blocks(self, text: str):
        """Divide el markdown en bloques por cabecera de caso."""
        blocks = []

        # Intentar con el primer patrón (formato con nombre entre comillas)
        for pattern in self.CASE_HEADER_PATTERNS:
            parts = pattern.split(text)
            if len(parts) > 1:
                # parts alterna: [preambulo, num, nombre, subtitulo?, body, num, ...]
                step = pattern.groups if hasattr(pattern, 'groups') else 3
                # Detectar cuántos grupos captura
                test_match = pattern.search(text)
                if test_match:
                    n_groups = len(test_match.groups())
                    step = n_groups + 1
                    for i in range(1, len(parts), step):
                        if i + n_groups - 1 < len(parts):
                            num = parts[i].strip()
                            name = parts[i + 1].strip() if n_groups >= 2 else ""
                            subtitle = parts[i + 2].strip() if n_groups >= 3 else ""
                            body = parts[i + n_groups] if i + n_groups < len(parts) else ""
                            blocks.append((num, name, subtitle, body))
                    break

        return blocks

    def _parse_case_body(self, num: str, name: str, subtitle: str, body: str) -> Optional[Dict]:
        verdict_match = self.VERDICT_RE.search(body)
        if not verdict_match:
            # Intentar buscar en nombre/subtítulo también
            combined = f"{name} {subtitle} {body}"
            verdict_match = self.VERDICT_RE.search(combined)
        if not verdict_match:
            return None

        verdict = verdict_match.group(1).upper()
        if verdict not in VERDICTS_ALLOWED:
            return None

        confidence_str = verdict_match.group(2)
        confidence = int(confidence_str) if confidence_str else 90

        signals = self._extract(self.SIGNALS_RE, body)
        carnegie = self._extract(self.CARNEGIE_RE, body)
        peirce_raw = self._extract(self.PEIRCE_RE, body)
        grice = self._extract(self.GRICE_RE, body)
        eco = self._extract(self.ECO_RE, body)
        interpretation = self._extract(self.INTERPRETATION_RE, body)

        artifacts = self._signals_to_artifacts(signals, peirce_raw)
        peirce = self._parse_peirce(peirce_raw, signals, grice, carnegie)

        case_id = f"VIGIA-SYN-{int(num):03d}"
        full_name = name
        if subtitle:
            full_name = f"{name} – {subtitle}"

        return {
            "case_id": case_id,
            "case_name": full_name.strip(),
            "source_origin": "synthetic_markdown",
            "source_dataset": "VIGÍA Internal Corpus",
            "description": (interpretation or f"Caso sintético {num}: {name}").strip()[:500],
            "expected_verdict": verdict,
            "confidence_expected": confidence,
            "expected_mitre_ttps": [],
            "carnegie_pattern_expected": carnegie[:80].strip() if carnegie else None,
            "grice_violation": grice[:80].strip() if grice else None,
            "eco_signal": eco[:80].strip() if eco else None,
            "artifacts": artifacts,
            "peirce_expected": peirce,
            "devil_advocate": DEVIL_ADVOCATE_TEMPLATES.get(verdict, ""),
            "abstention_risk": "bajo",
            "_parser": "markdown_v2.3",
        }

    def _extract(self, pattern: re.Pattern, text: str) -> Optional[str]:
        m = pattern.search(text)
        return m.group(1).strip() if m else None

    def _signals_to_artifacts(self, signals: Optional[str], peirce: Optional[str]) -> List[Dict]:
        if not signals:
            return [{
                "artifact_id": "ART-001",
                "type": "file_metadata",
                "content": "Artefacto sin señales explícitas detectadas.",
                "forensic_anomalies": ["Requiere análisis manual"],
                "peirce_layer": "FIRSTNESS",
            }]

        # Separar por oraciones o bullets
        lines = [l.strip() for l in re.split(r'\.\s+|\n+', signals) if l.strip() and len(l.strip()) > 10]
        artifacts = []
        for i, line in enumerate(lines[:5], 1):
            artifacts.append({
                "artifact_id": f"ART-{i:03d}",
                "type": self._detect_type(line),
                "content": line[:400],
                "forensic_anomalies": self._extract_anomalies(line),
                "peirce_layer": "FIRSTNESS" if i == 1 else ("SECONDNESS" if i <= 3 else "THIRDNESS"),
            })
        return artifacts

    def _detect_type(self, line: str) -> str:
        l = line.lower()
        if any(w in l for w in ["bash", "historial", "history", "comando", "shell"]):
            return "bash_history"
        if any(w in l for w in ["log", "auth.log", "syslog", "journal"]):
            return "syslog"
        if any(w in l for w in ["mensaje", "slack", "ticket", "jira", "chat"]):
            return "slack_message"
        if any(w in l for w in ["ip", "dns", "network", "conexión", "netstat", "ping"]):
            return "network_flow"
        if any(w in l for w in ["pdf", "metadata", "exif", "imagen", "foto"]):
            return "file_metadata"
        if any(w in l for w in ["powershell", "ps1", "script"]):
            return "powershell_log"
        if any(w in l for w in ["timestamp", "hora", "fecha", "tiempo", "sesión"]):
            return "timestamp"
        if any(w in l for w in ["registro", "registry", "hive"]):
            return "registry"
        return "file_metadata"

    def _extract_anomalies(self, line: str) -> List[str]:
        anomalies = []
        l = line.lower()
        if any(w in l for w in ["contradice", "contradicción", "inconsistencia", "disonancia"]):
            anomalies.append("Contradicción entre señal y contexto")
        if any(w in l for w in ["cirílico", "ruso", "layout", "кщще", "ghbdtn"]):
            anomalies.append("Desliz de teclado — atribución lingüística")
        if any(w in l for w in ["3am", "3:00", "3am", "nocturno", "noche", "madrugada"]):
            anomalies.append("Actividad fuera del patrón circadiano")
        if any(w in l for w in ["borrar", "eliminar", "suprimir", "destruir", "limpiar"]):
            anomalies.append("Destrucción de evidencia potencial")
        if any(w in l for w in ["urgente", "urgencia", "inmediatamente", "ya mismo"]):
            anomalies.append("Presión temporal artificial")
        if not anomalies:
            anomalies.append("Anomalía detectada por análisis semiótico — requiere verificación")
        return anomalies[:3]

    def _parse_peirce(self, raw: Optional[str], signals: Optional[str],
                      grice: Optional[str], carnegie: Optional[str]) -> Dict[str, str]:
        peirce = {
            "firstness": signals[:200] if signals else "Observación inicial de la evidencia.",
            "secondness": grice[:200] if grice else "Contradicción indexical en los artefactos.",
            "thirdness": carnegie[:200] if carnegie else "Interpretación simbólica de la intención.",
        }
        if raw:
            raw_lower = raw.lower()
            if any(k in raw_lower for k in ["primeridad", "firstness", "rastro físico", "primer"]):
                peirce["firstness"] = raw[:300]
            if any(k in raw_lower for k in ["segundidad", "secondness", "contradicción", "index"]):
                peirce["secondness"] = raw[:300]
            if any(k in raw_lower for k in ["terceridad", "thirdness", "símbolo", "ley", "hábito"]):
                peirce["thirdness"] = raw[:300]
        return peirce


# ── Validador ─────────────────────────────────────────────────────────────

class CaseValidator:
    def __init__(self):
        self.errors: List[str] = []

    def validate(self, case: Dict[str, Any]) -> bool:
        self.errors = []

        for field in REQUIRED_FIELDS:
            if field not in case or case[field] is None:
                self.errors.append(f"Campo requerido ausente: {field}")

        if "expected_verdict" in case:
            v = case["expected_verdict"].upper() if isinstance(case["expected_verdict"], str) else ""
            if v not in VERDICTS_ALLOWED:
                self.errors.append(f"Veredicto inválido: {case['expected_verdict']}")

        if "confidence_expected" in case:
            c = case["confidence_expected"]
            if not isinstance(c, (int, float)) or not (0 <= c <= 100):
                self.errors.append(f"Confianza fuera de rango: {c}")

        if "artifacts" in case and isinstance(case["artifacts"], list):
            if len(case["artifacts"]) == 0:
                self.errors.append("Lista de artefactos vacía")

        return len(self.errors) == 0


# ── Motor de consolidación ────────────────────────────────────────────────

class ConsolidationEngine:
    def __init__(self, output_dir: str, validate: bool = False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.validator = CaseValidator()
        self.validate_mode = validate
        self.seen_hashes: set = set()
        self.stats = {
            "parsed": 0, "valid": 0,
            "invalid": 0, "deduplicated": 0, "written": 0,
        }

    def add_cases(self, cases: List[Dict[str, Any]], source: str):
        for case in cases:
            self.stats["parsed"] += 1

            # Normalizar veredicto
            if "expected_verdict" in case and isinstance(case["expected_verdict"], str):
                case["expected_verdict"] = case["expected_verdict"].upper()

            # Metadatos de consolidación
            case["_consolidation"] = {
                "source_file": str(source),
                "consolidated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Validar
            if self.validate_mode:
                if not self.validator.validate(case):
                    self.stats["invalid"] += 1
                    cid = case.get("case_id", "UNKNOWN")
                    print(f"  [INVALID] {cid}: {'; '.join(self.validator.errors)}")
                    continue

            # Deduplicar
            h = _content_hash({
                k: v for k, v in case.items()
                if k not in ("_consolidation",)
            })
            if h in self.seen_hashes:
                self.stats["deduplicated"] += 1
                print(f"  [DEDUP] {case.get('case_id', 'UNKNOWN')} (hash {h})")
                continue

            self.seen_hashes.add(h)
            self.stats["valid"] += 1
            self._write_case(case)

    def _write_case(self, case: Dict[str, Any]):
        filename = f"{case['case_id']}.json"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(case, f, indent=2, sort_keys=True, ensure_ascii=False)
        self.stats["written"] += 1
        print(f"  [OK] {case['case_id']} → {filepath.name}")

    def write_index(self):
        case_files = sorted(self.output_dir.glob("*.json"),
                           key=lambda p: p.stem)
        index = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "total_cases": self.stats["written"],
            "statistics": self.stats,
            "case_ids": [p.stem for p in case_files if not p.stem.startswith("_")],
        }
        index_path = self.output_dir / "_index.json"
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, sort_keys=True, ensure_ascii=False)
        print(f"\n[Index] {index_path} ({index['total_cases']} casos)")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("  RESUMEN DE CONSOLIDACIÓN")
        print("=" * 60)
        for k, v in self.stats.items():
            print(f"  {k:<20}: {v}")
        print(f"  {'output_dir':<20}: {self.output_dir}")
        print("=" * 60)


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Consolida casos forenses VIGÍA de múltiples fuentes"
    )
    parser.add_argument("--md-sources", nargs="*", default=[],
                        help="Archivos Markdown con casos narrativos")
    parser.add_argument("--json-sources", nargs="*", default=[],
                        help="Directorios o archivos JSON estructurados")
    parser.add_argument("--json-legacy", nargs="*", default=[],
                        help="Casos JSON legacy ya existentes")
    parser.add_argument("--output", required=True,
                        help="Directorio de salida")
    parser.add_argument("--validate", action="store_true",
                        help="Validar estrictamente contra esquema canónico")
    args = parser.parse_args()

    engine = ConsolidationEngine(args.output, validate=args.validate)
    md_parser = MarkdownCaseParser()

    # 1. Parsear Markdown
    for md_path in (args.md_sources or []):
        p = Path(md_path)
        if not p.exists():
            print(f"[WARN] {md_path} no encontrado, omitiendo.", file=sys.stderr)
            continue
        print(f"\n[MD] Parseando {p.name}...")
        cases = md_parser.parse_file(md_path)
        print(f"     → {len(cases)} casos encontrados")
        engine.add_cases(cases, source=md_path)

    # 2. Ingerir JSON estructurado
    for json_source in (args.json_sources or []):
        path = Path(json_source)
        files = list(path.glob("*.json")) if path.is_dir() else [path]
        for json_file in sorted(files):
            if json_file.name.startswith("_"):
                continue
            print(f"\n[JSON] Ingiriendo {json_file.name}...")
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cases = data if isinstance(data, list) else [data]
                engine.add_cases(cases, source=str(json_file))
            except Exception as e:
                print(f"  [ERROR] {json_file.name}: {e}", file=sys.stderr)

    # 3. Ingerir JSON legacy
    for legacy in (args.json_legacy or []):
        path = Path(legacy)
        files = list(path.glob("*.json")) if path.is_dir() else [path]
        for json_file in sorted(files):
            if json_file.name.startswith("_"):
                continue
            print(f"\n[LEGACY] Ingiriendo {json_file.name}...")
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cases = data if isinstance(data, list) else [data]
                engine.add_cases(cases, source=f"legacy:{json_file}")
            except Exception as e:
                print(f"  [ERROR] {json_file.name}: {e}", file=sys.stderr)

    engine.write_index()
    engine.print_summary()


if __name__ == "__main__":
    main()
