"""
M1 regression tests — TCV fires on structured fields only.

Ref: docs/FOSSIL_HUNT_20260711.md (mechanism M1). The TCV rule must:
  - fire when BOTH structured event times exist and net < proc;
  - NOT fire from free-text description matching ("network", or "red" as a
    substring of words like "registered"/"flickered"/"credentials");
  - NOT fire from the generic artifact timestamp (collection time);
  - NOT fire from the _utcnow() default on artifacts with no timestamps
    (VIGIA-REAL-006 fabricated-fracture scenario);
  - NOT fire when the causal order is sane (net >= proc).
"""

from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact


def _tcvs(*artifacts):
    engine = CrossArtifactIncongruenceEngine()
    for a in artifacts:
        engine.add_artifact(a)
    return [f for f in engine.detect_fractures()
            if f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION"]


def _proc(creation_time=None, **kw):
    md = dict(kw.pop("metadata", {}))
    if creation_time is not None:
        md["process_creation_time"] = creation_time
    return Artifact(
        source_tool="vol3_pslist",
        evidence_type="memory_process",
        raw_score=0.6,
        description=kw.pop("description", "process object in memory"),
        metadata=md,
        **kw,
    )


def _net(log_time=None, **kw):
    md = dict(kw.pop("metadata", {}))
    if log_time is not None:
        md["network_log_time"] = log_time
    return Artifact(
        source_tool="zeek_conn",
        evidence_type="log_entry",
        raw_score=0.6,
        description=kw.pop("description", "outbound connection log"),
        metadata=md,
        **kw,
    )


class TestTCVStructuredOnly:

    def test_fires_on_structured_pair_net_before_proc(self):
        frs = _tcvs(
            _net(log_time="2026-04-10T10:00:00Z"),
            _proc(creation_time="2026-04-10T10:00:05Z"),
        )
        assert len(frs) == 1
        assert float(frs[0].severity) == 1.0

    def test_silent_when_causal_order_is_sane(self):
        frs = _tcvs(
            _net(log_time="2026-04-10T10:00:10Z"),
            _proc(creation_time="2026-04-10T10:00:05Z"),
        )
        assert frs == []

    def test_description_substring_network_does_not_qualify(self):
        # Pre-M1, "network" in the description made ANY artifact a network
        # event and its generic timestamp entered the comparison.
        frs = _tcvs(
            _net(log_time=None,
                 description="RDP enabled with Network Level Authentication disabled",
                 timestamp="2020-02-14T19:42:21Z"),
            _proc(creation_time="2020-04-20T23:19:17Z"),
        )
        assert frs == []

    def test_description_substring_red_does_not_qualify(self):
        # "registered" contains "red" — the VIGIA-FN-001 fossil: a vacation
        # request log classified as network activity.
        frs = _tcvs(
            _net(log_time=None,
                 description="marketing_user registered vacation from 2026-06-15",
                 timestamp="2026-06-14T00:00:00Z"),
            _proc(creation_time="2026-06-15T14:00:00Z"),
        )
        assert frs == []

    def test_generic_timestamp_fallback_removed_on_proc_side(self):
        # A memory_process without process_creation_time never enters the
        # rule, even if its collection timestamp would "violate" causality.
        frs = _tcvs(
            _net(log_time="2020-02-14T19:42:21Z"),
            _proc(creation_time=None, timestamp="2020-04-20T23:19:17Z"),
        )
        assert frs == []

    def test_utcnow_default_cannot_fabricate_fracture(self):
        # VIGIA-REAL-006: two artifacts with NO timestamps at all received
        # _utcnow() defaults milliseconds apart and produced a severity-1.0
        # TCV out of object-creation skew.
        frs = _tcvs(
            _net(log_time=None, description="file stored unencrypted on Desktop"),
            _proc(creation_time=None),
        )
        assert frs == []

    def test_out_of_range_timestamp_still_treated_as_missing(self):
        # R3-1 range guard remains active on the structured field.
        frs = _tcvs(
            _net(log_time="1970-01-01T00:00:00Z"),
            _proc(creation_time="2026-04-10T10:00:05Z"),
        )
        assert frs == []
