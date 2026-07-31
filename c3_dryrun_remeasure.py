#!/usr/bin/env python3
"""
c3_dryrun_remeasure.py
======================
Re-mide el impacto de NarrativeAuditor sobre el corpus real de bundles.

Emite:
    - narrativas analizadas
    - narrativas marcadas (is_clean=False)
    - threats totales, desglose por tipo
    - eventos CRITICAL_NARRATIVE_INJECTION (veredicto MALICE/INTENT)
    - ejemplos de cada threat_type para inspección manual

Uso:
    PYTHONPATH=$(pwd) python3 c3_dryrun_remeasure.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from vigia.core.narrative_auditor import NarrativeAuditor

CORPUS_DIR = Path("results")
BUNDLE_GLOB = "**/*_agent_bundle.json"


def _verdict(bundle: dict) -> str | None:
    """Busca el veredicto consolidado en las claves usadas por los bundles."""
    for key in ("agent_verdict", "overall_verdict", "caie_verdict", "verdict"):
        if key in bundle and bundle[key]:
            return str(bundle[key]).upper()
    return None


def main() -> int:
    auditor = NarrativeAuditor(strict_mode=True)
    bundles = sorted(CORPUS_DIR.glob(BUNDLE_GLOB))

    total_narratives = 0
    flagged_narratives = 0
    total_threats = 0
    threat_type_counts: Counter = Counter()
    critical_events = 0
    examples: dict[str, list[tuple[str, int, str]]] = {}

    for bundle_path in bundles:
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"SKIP {bundle_path.name}: {exc}", file=sys.stderr)
            continue

        narrative_text = bundle.get("narrative")
        if not isinstance(narrative_text, str) or not narrative_text.strip():
            continue

        narrative_lines = narrative_text.splitlines()
        total_narratives += 1

        inv_id = bundle.get("case_id") or bundle_path.stem
        result = auditor.audit(narrative_lines, investigation_id=inv_id)

        if not result.is_clean:
            flagged_narratives += 1
            total_threats += len(result.threats_detected)
            verdict = _verdict(bundle)
            would_invalidate = verdict in ("MALICE", "INTENT")
            if would_invalidate:
                critical_events += 1

            for threat in result.threats_detected:
                threat_type_counts[threat.pattern_type] += 1
                bucket = examples.setdefault(threat.pattern_type, [])
                if len(bucket) < 5:
                    bucket.append((
                        inv_id,
                        threat.line_index,
                        threat.matched_text,
                    ))

    print(f"Bundles con narrative: {total_narratives}")
    print(f"Narrativas marcadas:   {flagged_narratives} "
          f"({flagged_narratives / max(total_narratives, 1) * 100:.1f}%)")
    print(f"Threats totales:       {total_threats}")
    print(f"Eventos CRITICAL:      {critical_events}")
    print()
    print("Desglose por tipo de threat:")
    for ttype, count in threat_type_counts.most_common():
        print(f"  {ttype:<22} {count:>4}")
    print()
    print("Ejemplos (hasta 5 por tipo):")
    for ttype, items in sorted(examples.items()):
        print(f"\n{ttype}:")
        for inv_id, line_idx, matched in items:
            print(f"  - {inv_id} línea {line_idx}: {matched!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
