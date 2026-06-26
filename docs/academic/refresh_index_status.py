#!/usr/bin/env python3
"""
refresh_index_status.py
=======================
Updates the "Idiomas" column in ACADEMIC_DOCS_MASTER_INDEX.md and
ACADEMIC_DOCS_MASTER_INDEX_EN.md to reflect the actual language sections
present in each file.

Run from docs/academic/:
    python3 refresh_index_status.py
"""
import os
import re
import sys


ACADEMIC = os.path.dirname(os.path.abspath(__file__))


def actual_langs(path: str) -> str:
    """Return 'EN/ES/RU/ZH' string showing which sections exist in the file."""
    if not os.path.exists(path):
        return "—"
    content = open(path, encoding="utf-8").read()
    has_en = bool(
        re.search(r"(?m)^#{0,3}\s*ENGLISH\b", content)
        or re.search(r"(?m)^#{0,3}\s*English:", content)
    )
    has_es = bool(
        re.search(r"(?m)^#{0,3}\s*ESPA[ÑN]OL\b", content)
        or re.search(r"(?m)^#{0,3}\s*Español:", content)
    )
    has_ru = bool(re.search(r"(?m)^#{0,3}\s*РУС[СС]КИЙ\b", content))
    has_zh = bool(re.search(r"(?m)^#{0,3}\s*中文\b", content))
    parts = [l for l, v in [("EN", has_en), ("ES", has_es), ("RU", has_ru), ("ZH", has_zh)] if v]
    return "/".join(parts) if parts else "—"


def update_index(index_path: str) -> tuple[int, int]:
    """Update Idiomas column in one index file. Returns (rows_checked, rows_updated)."""
    content = open(index_path, encoding="utf-8").read()
    lines = content.splitlines(keepends=True)

    # Pattern: table row with a markdown link and a language tag at end
    # | `module.py` | [doc.md](path/doc.md) | EN/ES/RU |
    row_re = re.compile(
        r"^(\|[^|]+\|\s*\[[^\]]+\]\(([^)]+)\)\s*\|\s*)([A-Z/ZH—]+)(\s*\|)\s*$"
    )

    checked = 0
    updated = 0
    new_lines = []
    for line in lines:
        m = row_re.match(line)
        if m:
            checked += 1
            prefix = m.group(1)
            rel_href = m.group(2)
            old_langs = m.group(3).strip()
            suffix = m.group(4)

            full_path = os.path.join(ACADEMIC, rel_href)
            new_langs = actual_langs(full_path)

            if new_langs != old_langs:
                updated += 1
                new_lines.append(f"{prefix}{new_langs}{suffix}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Rebuild incomplete-docs section and stats
    new_content = "".join(new_lines)

    # Refresh the stats block
    all_docs_langs = []
    for subdir in os.listdir(ACADEMIC):
        subpath = os.path.join(ACADEMIC, subdir)
        if not os.path.isdir(subpath):
            continue
        for fname in os.listdir(subpath):
            if not fname.endswith(".md"):
                continue
            langs = actual_langs(os.path.join(subpath, fname))
            all_docs_langs.append(langs)

    total = len(all_docs_langs)
    complete = sum(1 for l in all_docs_langs if l == "EN/ES/RU/ZH")
    en_only = sum(1 for l in all_docs_langs if l == "EN")
    zh_only = sum(1 for l in all_docs_langs if l == "ZH")

    # Replace stats table values
    new_content = re.sub(
        r"(\| Total documentos \|\s*)[\d~]+",
        f"\\g<1>{total}",
        new_content,
    )
    new_content = re.sub(
        r"(\| Cobertura EN/ES/RU/ZH completa \|\s*)~?[\d]+ docs \(~?[\d]+%\)",
        f"\\g<1>{complete} docs ({complete*100//total if total else 0}%)",
        new_content,
    )

    open(index_path, "w", encoding="utf-8").write(new_content)
    return checked, updated


if __name__ == "__main__":
    for index_name in ["ACADEMIC_DOCS_MASTER_INDEX.md", "ACADEMIC_DOCS_MASTER_INDEX_EN.md"]:
        index_path = os.path.join(ACADEMIC, index_name)
        if not os.path.exists(index_path):
            print(f"Not found: {index_name}")
            continue
        checked, updated = update_index(index_path)
        print(f"{index_name}: {checked} rows checked, {updated} updated")
