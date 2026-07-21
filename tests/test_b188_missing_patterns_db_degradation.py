"""B-188 — an unavailable pattern DB must fail closed without creating it."""
from __future__ import annotations

from pathlib import Path

import pytest

from vigia.core.semiotic_detector_v2 import SemioticDetectorV2


def test_b188_missing_pattern_database_fails_closed_without_creating_it(
    tmp_path: Path,
) -> None:
    missing_db = tmp_path / "acquired" / "forensic_patterns.sqlite"

    with pytest.raises(RuntimeError, match="pattern database unavailable"):
        SemioticDetectorV2(str(missing_db))

    assert not missing_db.exists()
