"""
vigia/core/case_linkage.py
F2 (L-029 / FW-009) — deterministic cross-bundle linkage records.

Batch-level pass (invoked beside check_label_consistency in
run_all_agent.py): groups corpus cases by the artifact-metadata
case_origin join key and emits one signed record per group of >=2
distinct member files, so the cross-bundle relationship (the only place
a DARVO role inversion is expressible — L-029 root cause 1) is on the
record without touching any verdict.

Hardening baked in (dossier §5-F2 + Kimi's audit + judge 12):
  - copy-dedup by artifact-array SHA256: KIWI-004/005 are
    artifact-identical to KIWI-003 — without this rule one expediente
    emits multiple linkages against duplicated evidence (the L-016
    violation the design itself lists as a demote trigger);
  - artifact_id collision caveat: RT-FN-COLLUSION-001 already carries
    case_origin MPF7779408 with KIWI-006's artifact_ids reused verbatim —
    the forged-join-key attack is in-repo, and a group containing it must
    be flagged, never certified clean;
  - label-blind by construction (expected_verdict is never read);
  - NO timestamps inside the record — deterministic, order-independent
    replay; HMAC-SHA256 seal over the canonical record when
    VIGIA_HMAC_KEY[_FILE] is set;
  - records carry NO verdict authority, stated in the record itself.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.tools.paired_review import artifact_case_origin

LINKAGE_CAVEATS = (
    "This linkage record carries NO verdict authority: the join keys "
    "(case_origin, framing) are examiner-authored input (L-004 narrative "
    "class).",
    "Absence of linkage proves nothing — an aggressor filing through "
    "their own examiner omits or alters case_origin.",
    "Members sharing one provenance channel are ONE source seen N times, "
    "not mutual corroboration (L-016).",
)


def _canonical(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _resolve_hmac_key() -> Optional[bytes]:
    key = os.environ.get("VIGIA_HMAC_KEY")
    if key:
        return key.encode("utf-8")
    key_file = os.environ.get("VIGIA_HMAC_KEY_FILE")
    if key_file and Path(key_file).exists():
        return Path(key_file).read_bytes().strip()
    return None


def emit_linkage_records_data(
    named_cases: List[Tuple[str, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Emit linkage records from (stem, case_dict) pairs.

    Deterministic: members sorted by stem, no timestamps, HMAC over the
    canonical record. Never reads expected_verdict.
    """
    named = sorted(
        (t for t in named_cases if isinstance(t[1], dict)),
        key=lambda t: t[0],
    )
    groups: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
    for stem, data in named:
        origin = artifact_case_origin(data)
        if origin is None:
            continue
        groups.setdefault(origin, []).append((stem, data))

    records: List[Dict[str, Any]] = []
    for origin in sorted(groups):
        entries = groups[origin]
        if len(entries) < 2:
            continue

        members: List[Dict[str, Any]] = []
        copies: List[Dict[str, Any]] = []
        first_stem_by_hash: Dict[str, str] = {}
        member_data: List[Tuple[str, Dict[str, Any]]] = []
        for stem, data in entries:
            art_hash = hashlib.sha256(
                _canonical(data.get("artifacts", []))
            ).hexdigest()
            if art_hash in first_stem_by_hash:
                copies.append({
                    "stem": stem,
                    "case_id": data.get("case_id"),
                    "copy_of": first_stem_by_hash[art_hash],
                    "artifact_set_sha256": art_hash,
                })
                continue
            first_stem_by_hash[art_hash] = stem
            members.append({
                "stem": stem,
                "case_id": data.get("case_id"),
                "framing": data.get("framing"),
                "artifact_set_sha256": art_hash,
            })
            member_data.append((stem, data))

        caveats = list(LINKAGE_CAVEATS)
        # Duplicated evidence is ALWAYS on the record, never adjudicated:
        # KIWI-004/005 declare themselves copies of 003, RT-FN-COLLUSION-001
        # does not (that IS the collusion pattern) — but "declares itself a
        # copy" is narrative too, so the record reports the fact and refuses
        # corroboration in both cases, judging no intent.
        if copies:
            caveats.append(
                "artifact-set collision: "
                + ", ".join(
                    f"{c['stem']} duplicates {c['copy_of']}" for c in copies
                )
                + " — duplicated evidence is ONE source, never "
                "corroboration (L-016; RT-FN-COLLUSION-001 fixture class)."
            )
        id_owner: Dict[str, str] = {}
        collisions: set = set()
        for stem, data in member_data:
            for a in data.get("artifacts", []):
                aid = a.get("artifact_id") if isinstance(a, dict) else None
                if not aid:
                    continue
                if aid in id_owner and id_owner[aid] != stem:
                    collisions.add(aid)
                id_owner.setdefault(aid, stem)
        if collisions:
            caveats.append(
                "artifact_id collision across DISTINCT case files "
                f"({', '.join(sorted(collisions))}): forged or duplicated "
                "join-key evidence — do NOT treat this group as "
                "corroboration (RT-FN-COLLUSION-001 fixture class)."
            )

        actor_a_pov = next(
            (m["stem"] for m in members
             if m.get("framing") == "perspective_actor_a"), None)
        actor_b_pov = next(
            (m["stem"] for m in members
             if m.get("framing") == "perspective_actor_b"), None)
        primary_pair = (
            {"actor_a_pov": actor_a_pov, "actor_b_pov": actor_b_pov}
            if actor_a_pov and actor_b_pov else None
        )

        record: Dict[str, Any] = {
            "schema": "linkage_v1",
            "case_origin": origin,
            "members": members,
            "copies": copies,
            "primary_pair": primary_pair,
            "caveats": caveats,
            "verdict_authority": "none",
        }
        digest = hashlib.sha256(_canonical(record)).hexdigest()
        record["record_sha256"] = digest
        key = _resolve_hmac_key()
        if key:
            record["record_hmac"] = hmac.new(
                key, digest.encode("utf-8"), hashlib.sha256
            ).hexdigest()
        records.append(record)
    return records


def emit_linkage_records(paths: List[Any]) -> List[Dict[str, Any]]:
    """Load case JSONs from paths and emit linkage records."""
    named: List[Tuple[str, Dict[str, Any]]] = []
    for p in paths:
        p = Path(p)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict):
            named.append((p.stem, data))
    return emit_linkage_records_data(named)


def write_linkage_records(
    records: List[Dict[str, Any]], out_dir: Any
) -> int:
    """Write one JSON file per record under out_dir. Returns count."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for rec in records:
        name = f"linkage_{rec['case_origin']}.json"
        (out / name).write_text(
            json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    return len(records)
