"""
vigia/sift/mft_timeline_analyzer.py

DEPRECATED: Use vigia.sift.disk_forensics.MFTTimelineAnalyzer instead.
This file exists for backward compatibility but redirects to the canonical implementation.
"""

from __future__ import annotations

# Re-export from canonical location
from vigia.sift.disk_forensics import (
    MFTTimelineAnalyzer,
    MFTAnalysisResult,
    MFTRecord,
)

__all__ = ["MFTTimelineAnalyzer", "MFTAnalysisResult", "MFTRecord"]
