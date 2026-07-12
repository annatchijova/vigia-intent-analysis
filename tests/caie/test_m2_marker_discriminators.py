"""
M2 regression tests — marker-class discriminators for Rule 1.

Ref: docs/M2_DISCRIMINATORS_DESIGN_20260711.md and docs/FOSSIL_HUNT_20260711.md
(mechanism M2, F-07..F-28). The invariants:

  - config-only cultural markers NEVER produce a fracture, without requiring
    explicit confirmed-clean False flags (H-02 guard inversion);
  - genuine linguistic-attribution markers fire LINGUISTIC_ATTRIBUTION_SIGNAL,
    never a planted-evidence theory;
  - social-engineering markers fire SOCIAL_ENGINEERING_PATTERN;
  - FALSE_FLAG_PATTERN requires manipulation evidence ON the markers
    ("high cultural + low technical" alone is not a planting theory);
  - Case C (real attack + contradicted attribution) is unchanged;
  - attribution evidence mis-typed as ip_geolocation/file_hash is rescued via
    metadata fields; plain network telemetry typed ip_geolocation is not
    culture and enters no marker branch;
  - unclassified markers (no analysis class in metadata) fire nothing.
"""

from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact


def _fractures(*artifacts):
    engine = CrossArtifactIncongruenceEngine()
    for a in artifacts:
        engine.add_artifact(a)
    return engine.detect_fractures()


def _types(frs):
    return {f.fracture_type for f in frs}


def _marker(raw=0.9, metadata=None, evidence_type="cultural_marker"):
    return Artifact(
        source_tool="sift_nlp",
        evidence_type=evidence_type,
        raw_score=raw,
        description="marker artifact",
        metadata=metadata or {},
    )


def _memory(raw=0.05, metadata=None):
    return Artifact(
        source_tool="vol3",
        evidence_type="memory_process",
        raw_score=raw,
        description="memory artifact",
        metadata=metadata or {},
    )


CONFIG_ONLY = {"cyrillic_filenames": 3, "keyboard_layout_detected": "RU",
               "timezone_offset": "+03:00", "language_confidence": 0.91}
GENUINE = {"linguistic_origin": "Russian", "calco_source": "стране",
           "intended_meaning": "area/section", "confidence": 0.91}
SOCIAL = {"tone": "defensive", "manager_appeal": True, "guilt_inversion": True}
BAIT = {"placement": "too_clean", "mismatch_with_technical_profile": True}


class TestConfigNativeDefault:

    def test_config_only_marker_fires_nothing_without_false_flags(self):
        # H-02 guard inversion: absence of manipulation evidence is the safe
        # default; the explicit timestomp_detected=False flags are no longer
        # required (the corpus negative controls do not carry them).
        frs = _fractures(_marker(raw=0.85, metadata=dict(CONFIG_ONLY)), _memory())
        assert "FALSE_FLAG_PATTERN" not in _types(frs)
        assert "LINGUISTIC_ATTRIBUTION_SIGNAL" not in _types(frs)
        assert "SOCIAL_ENGINEERING_PATTERN" not in _types(frs)


class TestGenuineAttribution:

    def test_genuine_marker_fires_linguistic_signal(self):
        frs = _fractures(_marker(metadata=dict(GENUINE)), _memory())
        assert "LINGUISTIC_ATTRIBUTION_SIGNAL" in _types(frs)
        assert "FALSE_FLAG_PATTERN" not in _types(frs)

    def test_linguistic_interpretation_never_asserts_planting(self):
        frs = _fractures(_marker(metadata=dict(GENUINE)), _memory())
        ling = [f for f in frs
                if f.fracture_type == "LINGUISTIC_ATTRIBUTION_SIGNAL"][0]
        text = ling.interpretation.lower()
        assert "planted" not in text.replace("no evidence-planting", "")
        assert "mislead attribution" not in text

    def test_mistyped_attribution_evidence_is_rescued(self):
        # Corpus reality: a keyboard-slip analysis typed ip_geolocation and a
        # stylometric analysis typed file_hash. The metadata decides.
        slip = _marker(raw=0.92, evidence_type="ip_geolocation",
                       metadata={"attribution_region": "RU/CIS",
                                 "matched_pattern": "кщще -> root"})
        stylo = _marker(raw=0.82, evidence_type="file_hash",
                        metadata={"ttr_similarity": 0.992, "style_entropy": 0.03})
        assert "LINGUISTIC_ATTRIBUTION_SIGNAL" in _types(_fractures(slip, _memory()))
        assert "LINGUISTIC_ATTRIBUTION_SIGNAL" in _types(_fractures(stylo, _memory()))

    def test_plain_ip_geolocation_telemetry_is_not_culture(self):
        netflow = _marker(raw=0.82, evidence_type="ip_geolocation",
                          metadata={"dest_ip": "185.220.101.42", "country": "BY",
                                    "duration_h": 72})
        frs = _fractures(netflow, _memory())
        assert _types(frs) & {"LINGUISTIC_ATTRIBUTION_SIGNAL",
                              "SOCIAL_ENGINEERING_PATTERN",
                              "FALSE_FLAG_PATTERN"} == set()


class TestSocialEngineering:

    def test_social_marker_fires_social_pattern(self):
        frs = _fractures(_marker(metadata=dict(SOCIAL)), _memory())
        assert "SOCIAL_ENGINEERING_PATTERN" in _types(frs)
        assert "FALSE_FLAG_PATTERN" not in _types(frs)

    def test_social_fields_do_not_rescue_non_cultural_types(self):
        # A testimony/log artifact mis-typed memory_process with social fields
        # must NOT enter the marker pool (only attribution/manip metadata
        # rescues a mis-typed artifact).
        testimony = _memory(raw=0.92, metadata={"tone": "defensive",
                                                "guilt_inversion": True})
        frs = _fractures(testimony, _memory())
        assert "SOCIAL_ENGINEERING_PATTERN" not in _types(frs)


class TestFalseFlagRequiresManipulation:

    def test_high_cultural_low_technical_alone_fires_nothing(self):
        # The pre-M2 fossil: any high marker + weak memory = "planted".
        unclassified = _marker(raw=0.91, metadata={"edr_product": "CS",
                                                   "alert_count": 12})
        frs = _fractures(unclassified, _memory(raw=0.05))
        assert "FALSE_FLAG_PATTERN" not in _types(frs)

    def test_bait_with_low_technical_fires_false_flag_pattern(self):
        frs = _fractures(_marker(metadata=dict(BAIT)), _memory(raw=0.05))
        assert "FALSE_FLAG_PATTERN" in _types(frs)

    def test_case_c_real_attack_plus_bait_unchanged(self):
        frs = _fractures(_marker(metadata=dict(BAIT)), _memory(raw=0.86))
        assert "FALSE_FLAG_ATTRIBUTION_MISMATCH" in _types(frs)
        assert "FALSE_FLAG_PATTERN" not in _types(frs)

    def test_confirmed_clean_still_suppresses_false_flag_pattern(self):
        clean_fs = Artifact(
            source_tool="sift_mft", evidence_type="mft_entry", raw_score=0.04,
            description="filesystem manipulation check",
            metadata={"timestomp_detected": False, "backdating_detected": False},
        )
        frs = _fractures(_marker(metadata=dict(BAIT)), _memory(raw=0.05), clean_fs)
        assert "FALSE_FLAG_PATTERN" not in _types(frs)
