"""vigia.report.strings — EN and ES tables must be provably in lockstep.

Mirrors tests/test_webui_endpoints.py::test_i18n_tables_have_identical_keys
for the Python-side tables. Also asserts that every key a renderer references
as a literal exists in both tables, that ``t()`` refuses unknown keys instead
of falling back, and that no emoji codepoint slipped into either table.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from vigia.report.strings import STRINGS, t

REPORT_DIR = Path(__file__).resolve().parent.parent / "vigia" / "report"

# t(lang, "key") / t(self.lang, "key") / t(lang, 'key')
_T_CALL = re.compile(r"""\bt\(\s*[\w.]+\s*,\s*(['"])([^'"]+)\1""")

# Emoji and pictographs; the repo forbids them in generated prose.
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")


def test_tables_have_identical_keys():
    assert set(STRINGS) == {"en", "es"}
    en, es = set(STRINGS["en"]), set(STRINGS["es"])
    assert en, "empty EN table"
    assert en == es, (
        f"only in en: {sorted(en - es)}; only in es: {sorted(es - en)}"
    )


def test_no_value_is_empty_or_identical_placeholder():
    for lang, table in STRINGS.items():
        for key, value in table.items():
            assert isinstance(value, str) and value.strip(), f"{lang}:{key} is empty"


def test_placeholders_match_between_languages():
    ph = re.compile(r"\{(\w+)\}")
    for key in STRINGS["en"]:
        assert set(ph.findall(STRINGS["en"][key])) == set(ph.findall(STRINGS["es"][key])), key


def test_every_literal_key_used_by_renderers_exists():
    referenced = set()
    for path in REPORT_DIR.glob("*.py"):
        if path.name == "strings.py":
            continue
        for _q, key in _T_CALL.findall(path.read_text(encoding="utf-8")):
            referenced.add(key)
    missing = sorted(k for k in referenced if k not in STRINGS["en"])
    assert not missing, f"renderers reference undefined keys: {missing}"


def test_t_refuses_unknown_key_and_language():
    with pytest.raises(KeyError):
        t("en", "no.such.key")
    with pytest.raises(KeyError):
        t("fr", "header.case")


def test_t_formats_placeholders():
    out = t("es", "footer.note", version="1.0", sha256="ab" * 32)
    assert "1.0" in out and "ab" * 32 in out


def test_no_emoji_in_either_table():
    for lang, table in STRINGS.items():
        for key, value in table.items():
            assert not _EMOJI.search(value), f"emoji in {lang}:{key}"


def test_sealed_vocabulary_is_not_translated():
    """Verdict tokens must appear as the literal token in the Spanish table too."""
    for token in ("NOISE", "SUSPICION", "INTENT", "MALICE", "ABSTAIN"):
        assert token in STRINGS["es"][f"scale.{token}.meaning"] or token in STRINGS["es"][
            f"notnot.{token}"
        ], token
    for bad in ("RUIDO", "SOSPECHA", "INTENCIÓN", "MALICIA", "ABSTENCIÓN"):
        for key, value in STRINGS["es"].items():
            assert bad not in value, f"translated verdict token in es:{key}"
