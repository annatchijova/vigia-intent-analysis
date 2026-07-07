#!/usr/bin/env python3
"""
complete_acquisition_metadata.py — Lote aditivo de metadata de adquisición
(WHAT_IS_NEXT §1.1.2, sesión 2026-07-07; precondición del dataset de
calibración de la Tanda C).

Doctrina (L-037): los campos ausentes degradan el trust HONESTAMENTE — por lo
tanto este script NO fabrica proveniencia física. Documenta la proveniencia
REAL de cada señal sintética/convertida:

  - acquisition_tool      : el método real (converter/migración de bundle
                            sellado, según `_migration_note`), o la declaración
                            explícita de caso de corpus sin adquisición física.
  - acquisition_hash      : sha256 del bundle FUENTE si existe en disco
                            (proveniencia verificable), si no sha256 del JSON
                            canónico del propio artefacto (auto-atestación).
                            `acquisition_note` declara qué cubre el hash.
  - acquisition_timestamp : fecha de `_migration_note` si existe; si no, la
                            fecha de esta documentación retroactiva.
  - write_blocker_used    : False — no hubo medio físico. Honesto.

Solo toca artefactos EBS (raw_score presente) que no sean
ACQUISITION_CONTEXT. No toca artefactos narrativos. Solo AGREGA campos
ausentes — nunca sobreescribe un valor existente.

Uso:
    python3 scripts/complete_acquisition_metadata.py [--dry-run]
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import run_all_agent as runner  # noqa: E402

RETRO_DATE = "2026-07-07"
ACQ = ("acquisition_tool", "acquisition_hash", "acquisition_timestamp")


def _is_ebs(art: dict) -> bool:
    return isinstance(art, dict) and "raw_score" in art


def _is_ctx(art: dict) -> bool:
    try:
        return (
            (float(art.get("prior_trust", 1) or 0) == 0.0
             and float(art.get("raw_score", 1) or 0) == 0.0)
            or art.get("role") == "ACQUISITION_CONTEXT_NOT_ATTACK_EVIDENCE"
        )
    except (TypeError, ValueError):
        return False


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_canonical(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()


def complete_case(path: Path, dry_run: bool = False) -> dict:
    case = json.loads(path.read_text(encoding="utf-8"))
    changes = []

    mig = case.get("_migration_note") or {}
    mig_date = mig.get("date")
    mig_method = mig.get("method")
    mig_source = mig.get("source")
    source_path = (REPO / mig_source) if mig_source else None
    source_exists = bool(source_path and source_path.exists())

    # Campos de raíz aditivos
    if "schema_version" not in case:
        case["schema_version"] = 1
        changes.append("root:schema_version=1")
    if "case_name" not in case and case.get("case_id"):
        case["case_name"] = case["case_id"]
        changes.append("root:case_name=case_id")

    if mig_method:
        tool = f"VIGIA deterministic pipeline — {mig_method[:160]}"
    else:
        tool = ("VIGIA corpus case (señal sintética/convertida — "
                "sin adquisición física)")
    ts = f"{mig_date}T00:00:00Z" if mig_date else f"{RETRO_DATE}T00:00:00Z"

    for art in case.get("artifacts", []):
        if not _is_ebs(art) or _is_ctx(art):
            continue
        meta = art.get("metadata")
        if not isinstance(meta, dict):
            meta = {}
            art["metadata"] = meta
            changes.append(f"{art.get('artifact_id','?')}:metadata={{}}")
        aid = art.get("artifact_id", "?")

        missing = [f for f in ACQ if not meta.get(f)]
        if missing:
            if "acquisition_tool" in missing:
                meta["acquisition_tool"] = tool
            if "acquisition_timestamp" in missing:
                meta["acquisition_timestamp"] = ts
            if "acquisition_hash" in missing:
                if source_exists:
                    meta["acquisition_hash"] = f"sha256:{_sha256_file(source_path)}"
                    hash_covers = f"bundle fuente {mig_source}"
                else:
                    meta["acquisition_hash"] = (
                        f"sha256:{_sha256_canonical(art.get('description') or art)}"
                    )
                    hash_covers = "JSON canónico del propio artefacto (auto-atestación)"
                meta.setdefault(
                    "acquisition_note",
                    f"Metadata documentada retroactivamente ({RETRO_DATE}, "
                    f"WHAT_IS_NEXT §1.1.2). Sin adquisición física: caso de "
                    f"corpus. El hash cubre: {hash_covers}.",
                )
            changes.append(f"{aid}:acq+{','.join(missing)}")

        if meta.get("write_blocker_used") is None:
            meta["write_blocker_used"] = False
            changes.append(f"{aid}:write_blocker_used=False")

        if not art.get("provenance_chain"):
            chain = ["caso de corpus VIGÍA (JSON)"]
            if mig_method:
                chain.append(mig_method[:160])
            art["provenance_chain"] = chain
            changes.append(f"{aid}:provenance_chain")

    if changes and not dry_run:
        path.write_text(
            json.dumps(case, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {"case": path.stem, "changes": changes}


def main() -> int:
    dry = "--dry-run" in sys.argv
    touched, untouched = 0, 0
    for c in runner.find_cases(runner.CASES_DIRS):
        r = complete_case(c, dry_run=dry)
        if r["changes"]:
            touched += 1
            print(f"[{'DRY' if dry else 'MOD'}] {r['case']}: {len(r['changes'])} cambio(s)")
        else:
            untouched += 1
    print(f"\n{'DRY-RUN — ' if dry else ''}casos tocados: {touched} | sin cambios: {untouched}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
