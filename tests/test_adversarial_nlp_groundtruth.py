"""
tests/test_adversarial_nlp_groundtruth.py
=========================================
Ground-truth tests for vigia/tools/adversarial_nlp.py (was 0% covered).

adversarial_nlp is a deterministic linguistic-forensics module: it converts
text into z-scores, Zipf coefficients, readability indices and a "Multiplicador
de Certeza Pericial" (MCP) that feeds a court-facing forensic verdict. Every
number it emits has one mathematically correct value for a controlled input,
which makes it a good ground-truth target: a regression cannot hide behind
"looks plausible" when the entropy of a known distribution, the OLS slope of a
known point set, or the syllable count of a known word is fixed by definition.

Most tests here pin the correct behavior. Two classes are regression tests for
real defects found while writing these tests:

  * TestSignedZeroRegression -> BUG-NLP-001 (signed-zero leak) — FIXED at the
    source; the class now guards the fix.
  * TestL33tOOVUnreachable    -> BUG-NLP-002 (dead OOV heuristic) — still OPEN;
    left FAILING on purpose (not xfail'd) so the defect stays visible until it
    is fixed (the fix changes tokenizer output and needs threshold revalidation).

See each class docstring for the full analysis and suggested fix.
"""
from __future__ import annotations

import math

import pytest

from vigia.tools import adversarial_nlp as anlp
from vigia.tools.adversarial_nlp import (
    AuthorialBaseline,
    ConfigLoader,
    GriceanMannerAnalyzer,
    LanguageDetector,
    ROI_Analyzer,
    SDA_NominalizationAnalyzer,
    ZipfImperfectionAnalyzer,
    calculate_entropy_profile,
)
from vigia.tools.nlp_constants import InstitutionalEmitter, Language


# ---------------------------------------------------------------------------
# LanguageDetector.detect / get_profile
# ---------------------------------------------------------------------------

class TestLanguageDetector:
    """detect() scores EN/ES bigrams + function words; ES accents force Spanish."""

    def test_clear_english_is_english(self):
        text = ("The defendant and the plaintiff agreed to the terms of the "
                "contract in the court.")
        assert LanguageDetector.detect(text) == Language.ENGLISH

    def test_accented_spanish_is_spanish(self):
        # Any accented character adds +20 to the Spanish score by design.
        text = "La investigación pericial acreditó la fabricación del expediente."
        assert LanguageDetector.detect(text) == Language.SPANISH

    def test_unaccented_spanish_is_spanish(self):
        # Function words (la, del, que) still tip the balance to Spanish.
        text = ("La investigacion pericial acredito fehacientemente la "
                "fabricacion del expediente judicial que corresponde.")
        assert LanguageDetector.detect(text) == Language.SPANISH

    def test_empty_text_is_unknown(self):
        # No bigrams, no function words, no accents -> both scores 0 -> UNKNOWN.
        assert LanguageDetector.detect("") == Language.UNKNOWN

    def test_non_alphabetic_is_unknown(self):
        assert LanguageDetector.detect("12345 67890 !!! ...") == Language.UNKNOWN

    def test_get_profile_english_maps_to_english_profile(self):
        assert LanguageDetector.get_profile(Language.ENGLISH).code == "en"

    def test_get_profile_unknown_defaults_to_spanish(self):
        # Documented: Spanish is the default profile for SANS compliance.
        assert LanguageDetector.get_profile(Language.UNKNOWN).code == "es"
        assert LanguageDetector.get_profile(Language.SPANISH).code == "es"


# ---------------------------------------------------------------------------
# calculate_entropy_profile — Shannon entropy (log2) over word/char histograms
# ---------------------------------------------------------------------------

class TestEntropyProfile:
    def test_two_equiprobable_words_is_one_bit(self):
        # p = {0.5, 0.5} -> H = 1.0 bit.
        assert calculate_entropy_profile("alpha beta")["lexical_entropy"] == pytest.approx(1.0, abs=1e-9)

    def test_four_equiprobable_words_is_two_bits(self):
        got = calculate_entropy_profile("alpha beta gamma delta")["lexical_entropy"]
        assert got == pytest.approx(2.0, abs=1e-9)

    def test_char_entropy_matches_closed_form(self):
        # "alphabeta" -> a:3, l/p/h/b/e/t:1 each, total 9.
        total = 9
        expected = -((3 / total) * math.log2(3 / total)
                     + 6 * ((1 / total) * math.log2(1 / total)))
        assert calculate_entropy_profile("alpha beta")["char_entropy"] == pytest.approx(expected, abs=1e-9)

    def test_empty_text_is_zero(self):
        prof = calculate_entropy_profile("")
        assert prof["lexical_entropy"] == 0.0
        assert prof["char_entropy"] == 0.0

    def test_is_deterministic(self):
        t = "acredito la fabricacion del expediente judicial acredito"
        assert calculate_entropy_profile(t) == calculate_entropy_profile(t)


# ---------------------------------------------------------------------------
# ZipfImperfectionAnalyzer._fit_zipf — log-log OLS power-law fit
# ---------------------------------------------------------------------------

class TestZipfFit:
    def test_matches_ols_closed_form(self):
        # freqs 4,2,1 over ranks 1,2,3 (log(r+1)); OLS slope hand-verified.
        tokens = ["x"] * 4 + ["y"] * 2 + ["z"] * 1
        alpha, r2 = ZipfImperfectionAnalyzer._fit_zipf(tokens)
        assert alpha == pytest.approx(1.233662, abs=1e-6)
        assert r2 == pytest.approx(0.977654, abs=1e-6)

    def test_uniform_distribution_is_degenerate(self):
        # All freqs equal -> zero slope AND zero variance in y -> alpha=0, r2=0.
        alpha, r2 = ZipfImperfectionAnalyzer._fit_zipf(["aaa", "bbb", "ccc", "ddd"])
        assert (alpha, r2) == (0.0, 0.0)

    def test_fewer_than_three_types_returns_zero(self):
        # Guard: len(freq) < 3 -> (0.0, 0.0).
        assert ZipfImperfectionAnalyzer._fit_zipf(["a", "a", "b"]) == (0.0, 0.0)

    def test_alpha_is_non_negative(self):
        # alpha = -slope; sorted-descending freqs give negative slope -> alpha>=0.
        tokens = ["a"] * 10 + ["b"] * 5 + ["c"] * 3 + ["d"] * 2 + ["e"] * 1
        alpha, _ = ZipfImperfectionAnalyzer._fit_zipf(tokens)
        assert alpha >= 0.0


class TestZipfExtractOOV:
    """_extract_oov flags structurally anomalous tokens (heuristic OOV)."""

    def test_digit_letter_mix_is_oov_when_called_directly(self):
        # The documented first heuristic: l33tspeak (letter+digit) is OOV.
        assert ZipfImperfectionAnalyzer._extract_oov(["h4ck", "w0rd"], "es") == ["h4ck", "w0rd"]

    def test_double_a_o_u_vowel_is_oov(self):
        # Rule is [aou]{2,}; "book" has "oo" -> flagged.
        assert ZipfImperfectionAnalyzer._extract_oov(["book"], "es") == ["book"]

    def test_ee_vowel_is_not_flagged(self):
        # Rule intentionally excludes 'e'/'i'; "meet" ("ee") is not OOV.
        assert ZipfImperfectionAnalyzer._extract_oov(["meet"], "es") == []

    def test_consonant_cluster_is_oov(self):
        # "strength" -> 7 consonants / 8 chars = 0.875 > 0.75 -> OOV.
        assert ZipfImperfectionAnalyzer._extract_oov(["strength"], "es") == ["strength"]

    def test_clean_words_are_not_oov(self):
        assert ZipfImperfectionAnalyzer._extract_oov(["casa", "mesa", "perro"], "es") == []

    def test_insufficient_oov_reports_reason(self):
        # Fewer than _ZIPF_MIN_OOV_TOKENS anomalies -> INSUFFICIENT sentinel.
        res = ZipfImperfectionAnalyzer().analyze("hola casa mesa amigo dia")
        assert res["is_calculated_imperfection"] is False
        assert res["reason"].startswith("INSUFFICIENT_OOV_TOKENS")
        assert res["tool_name"] == "GCI"


# ---------------------------------------------------------------------------
# SDA_NominalizationAnalyzer — noun/verb classification by suffix
# ---------------------------------------------------------------------------

class TestSDANominalization:
    def setup_method(self):
        self.sda = SDA_NominalizationAnalyzer(ConfigLoader())

    def test_controlled_english_counts(self):
        # "investigation"/"examination" -> nouns (-tion); "running"/"walking" -> verbs (-ing).
        res = self.sda.analyze("investigation examination running walking",
                               InstitutionalEmitter.UNKNOWN, "en")
        assert res["counts"]["nouns"] == 2
        assert res["counts"]["verbs"] == 2
        # nv_ratio = nouns/max(verbs,1) = 1.0 ; nominalization = nouns/(n+v+a) = 0.5
        assert res["nv_ratio"] == pytest.approx(1.0, abs=1e-9)
        assert res["nominalization"] == pytest.approx(0.5, abs=1e-9)

    def test_empty_text_returns_zero_counts(self):
        res = self.sda.analyze("", InstitutionalEmitter.UNKNOWN, "en")
        assert res["counts"] == {"nouns": 0, "verbs": 0, "adjs": 0, "preps": 0}
        assert res["is_inconsistent"] is False
        assert res["fabrication_probability"] == 0.0


# ---------------------------------------------------------------------------
# ROI_Analyzer — Flesch score and Spanish syllable counter (closed form)
# ---------------------------------------------------------------------------

class TestROIReadability:
    def setup_method(self):
        self.roi = ROI_Analyzer(ConfigLoader())

    def test_flesch_en_closed_form(self):
        # 206.835 - 1.015*ASL - 84.6*ASW for a hand-countable sentence pair.
        text = "The cat sat on the mat. The dog ran to the park."
        # 12 words / 2 sentences -> ASL = 6.0 ; each word 1 syllable -> ASW = 1.0
        expected = 206.835 - 1.015 * 6.0 - 84.6 * 1.0
        assert self.roi._flesch_en(text) == pytest.approx(expected, abs=1e-9)

    def test_syllables_es_counts_vowel_groups(self):
        # in-ves-ti-ga-cion -> 5 vowel groups.
        assert self.roi._syllables_es("investigacion") == 5

    def test_syllables_es_minimum_one(self):
        # A consonant-only token still counts as one syllable.
        assert self.roi._syllables_es("xyz") == 1

    def test_empty_text_returns_no_obfuscation(self):
        res = self.roi.analyze("", InstitutionalEmitter.UNKNOWN, "en")
        assert res["is_obfuscation_attack"] is False
        assert res["obfuscation_type"] == "NONE"
        assert res["gunning_fog"] == 0.0


# ---------------------------------------------------------------------------
# GriceanMannerAnalyzer.count_syllables — vowel-group + silent-e heuristic
# ---------------------------------------------------------------------------

class TestGriceanSyllables:
    def setup_method(self):
        self.g = GriceanMannerAnalyzer()

    @pytest.mark.parametrize("word,expected", [
        ("the", 1),        # one vowel group
        ("make", 1),       # 2 groups, silent-e drop -> 1
        ("code", 1),       # 2 groups, silent-e drop -> 1
        ("strength", 1),   # single vowel group
        ("running", 2),    # u, i -> 2
    ])
    def test_english_syllable_counts(self, word, expected):
        assert self.g.count_syllables(word, Language.ENGLISH) == expected

    def test_empty_word_is_zero(self):
        assert self.g.count_syllables("", Language.ENGLISH) == 0


# ---------------------------------------------------------------------------
# AuthorialBaseline.update — incremental (Welford-style) running mean
# ---------------------------------------------------------------------------

class TestAuthorialBaseline:
    def test_running_mean_equals_arithmetic_mean(self):
        b = AuthorialBaseline("author-1")
        values = [0.5, 0.7, 0.9]
        for v in values:
            b.update(v, v, v)
        assert b.document_count == 3
        assert b.mean_ttr == pytest.approx(sum(values) / len(values), abs=1e-12)
        assert b.mean_lexical_entropy == pytest.approx(sum(values) / len(values), abs=1e-12)
        assert b.mean_zipf == pytest.approx(sum(values) / len(values), abs=1e-12)

    def test_first_update_sets_mean_exactly(self):
        b = AuthorialBaseline("author-2")
        b.update(0.42, 3.1, 1.05)
        assert b.mean_ttr == pytest.approx(0.42, abs=1e-12)
        assert b.document_count == 1

    def test_std_ttr_has_floor(self):
        b = AuthorialBaseline("author-3")
        for v in [0.5, 0.7, 0.9]:
            b.update(v, v, v)
        assert b.std_ttr >= 0.01


# ---------------------------------------------------------------------------
# ConfigLoader — default config, language config, institutional baselines
# ---------------------------------------------------------------------------

class TestConfigLoader:
    def setup_method(self):
        self.cfg = ConfigLoader()  # no path -> DEFAULT_CONFIG

    def test_institutional_baseline_values(self):
        base = self.cfg.get_institutional_baseline(InstitutionalEmitter.MPF)
        assert base.nv_ratio_mean == 3.2
        assert base.nv_ratio_std == 0.4

    def test_language_config_english(self):
        lc = self.cfg.get_language_config("en")
        assert lc.code == "en"
        assert "tion" in lc.noun_suffixes

    def test_unknown_language_falls_back_to_spanish_lexicon(self):
        # get() default is the Spanish config for any unmapped code.
        lc = self.cfg.get_language_config("xx")
        assert "el" in lc.function_words  # Spanish article present

    def test_unknown_emitter_uses_unknown_baseline(self):
        base = self.cfg.get_institutional_baseline(InstitutionalEmitter.FORENSIC_LAB)
        # FORENSIC_LAB has no dedicated baseline -> UNKNOWN block (mean 3.0).
        assert base.nv_ratio_mean == 3.0


# ===========================================================================
# REGRESSION GUARDS — BUG-NLP-001 fixed (below); BUG-NLP-002 still open, left
# failing on purpose (do not xfail)
# ===========================================================================

class TestSignedZeroRegression:
    """
    BUG-NLP-001 (FIXED) — signed-zero leak in calculate_entropy_profile. This
    class is now the regression guard for the fix.

    For any input whose word (or character) distribution is degenerate — a
    single type repeated, e.g. "foo foo foo" — the Shannon sum was
    -(1.0 * log2(1.0)) == -0.0, so calculate_entropy_profile returned
    lexical_entropy == -0.0 (IEEE 754 negative zero) instead of 0.0.

    -0.0 == 0.0 is True, so it is invisible to normal comparisons, but it is a
    determinism hazard identical in kind to the already-documented
    BUG-ENTROPY-001 (see tests/test_entropy_kernel_groundtruth.py): the bundle
    canonicalizer formats floats with a fixed-width decimal, and
    "-0.00000000" != "0.00000000". lexical_entropy flows from
    ForensicEngine.analyze into the ACP metrics dict ({"entropy": ...}) and the
    SQLite baseline / z-score path, so two mathematically identical
    zero-entropy documents can serialize to different bytes.

    Scope of confirmation:
      CONFIRMED at the function boundary — calculate_entropy_profile returns a
      negative zero for degenerate inputs (reproduced below and via probe).
      PLAUSIBLE end-to-end — whether the raw float reaches a sealed bundle
      field unrounded is not traced through the full ForensicEngine + CAIE path
      here (mirrors the scoping of BUG-ENTROPY-001).

    Repro:
      calculate_entropy_profile("foo foo foo")["lexical_entropy"] -> -0.0

    Fix applied: signed zero is normalized at the return site of
    calculate_entropy_profile (lexical_entropy + 0.0, char_entropy + 0.0, which
    map -0.0 -> 0.0). These tests assert the degenerate result is +0.0.
    """

    @pytest.mark.parametrize("text", ["foo foo foo", "aaa"])
    def test_degenerate_lexical_entropy_is_positive_zero(self, text):
        v = calculate_entropy_profile(text)["lexical_entropy"]
        assert v == 0.0  # sanity: it is numerically zero
        assert math.copysign(1.0, v) > 0.0, (
            f"lexical_entropy for {text!r} is signed-zero {v!r}; canonicalizes "
            f'to "-0.00000000" != "0.00000000" (BUG-NLP-001).'
        )


class TestL33tOOVUnreachable:
    """
    BUG-NLP-002 — the documented l33tspeak OOV heuristic is dead in analyze().

    ZipfImperfectionAnalyzer._extract_oov documents its FIRST out-of-vocabulary
    heuristic as "Mezcla digitos+letras (l33tspeak)" and correctly flags such
    tokens when called directly (see TestZipfExtractOOV). But the only public
    path, ZipfImperfectionAnalyzer.analyze(), first runs _tokenize(), whose
    regex matches word-boundary runs of letters (Spanish accents included) of
    length 3 or more only -- no digits.
    Every digit-bearing token is therefore split into sub-3-char letter runs and
    dropped BEFORE _extract_oov ever sees it, so the l33tspeak branch can never
    fire through analyze().

    Consequence: a document whose anomalies are exactly the artificial-error
    pattern this analyzer exists to catch (l33tspeak such as "h4ck3r m4lw4r3
    r00tk1t passw0rd") tokenizes to [] and is reported as
    INSUFFICIENT_OOV_TOKENS (n=0) — the analyzer stays silent on its own
    headline signal.

    Scope of confirmation:
      CONFIRMED — _tokenize("h4ck3r ...") returns [] (reproduced below and via
      probe), and _extract_oov flags the same tokens when handed them directly,
      proving the capability exists but is unreachable in the pipeline. Whether
      the intended contract is "analyze() must surface l33tspeak" is a design
      judgement, but the module's own docstring advertises it as the primary
      OOV heuristic, so the public behavior contradicts the documented feature.

    Repro:
      ZipfImperfectionAnalyzer()._tokenize("h4ck3r m4lw4r3") -> []
      ZipfImperfectionAnalyzer().analyze("h4ck3r m4lw4r3 r00tk1t passw0rd "
          "d3f4c3d 3xpl01t sh3llc0d3")["n_oov_tokens"] -> 0

    Suggested fix: either (a) allow digit-bearing tokens through _tokenize
    (a word-character regex with a bounded length keeps the ReDoS mitigation), or
    (b) run the l33tspeak detection on the raw text/whitespace split before the
    letters-only tokenizer strips the digits.
    """

    L33T = ("h4ck3r m4lw4r3 r00tk1t passw0rd d3f4c3d 3xpl01t sh3llc0d3 "
            "b0tn3t k3yl0gg3r r4ns0mw4r3")

    def test_tokenizer_strips_l33t_but_extract_oov_would_catch_it(self):
        # Half of the defect: the capability exists in isolation ...
        raw_tokens = self.L33T.split()
        assert ZipfImperfectionAnalyzer._extract_oov(raw_tokens, "es") == raw_tokens
        # ... but the pipeline tokenizer discards every one of them.
        assert ZipfImperfectionAnalyzer()._tokenize(self.L33T) == []

    @pytest.mark.xfail(
        strict=True,
        reason="BUG-NLP-002: l33tspeak OOV unreachable via analyze() — "
        "deferred D4, requires tokenizer revalidation",
    )
    def test_analyze_surfaces_l33tspeak_as_oov(self):
        # Intended contract per _extract_oov docstring: l33tspeak IS the primary
        # OOV signal, so a l33t-heavy document must not be dismissed as having
        # insufficient anomalies. Currently FAILS: n_oov == 0.
        # strict=True: si un fix del tokenizer lo hace pasar, el xfail truena
        # (XPASS) y obliga a retirar el marker junto con el cierre del bug.
        res = ZipfImperfectionAnalyzer().analyze(self.L33T)
        assert res["n_oov_tokens"] >= anlp._ZIPF_MIN_OOV_TOKENS, (
            "l33tspeak document tokenized to no OOV tokens; the documented "
            "digit+letter OOV heuristic is unreachable via analyze() "
            "(BUG-NLP-002)."
        )
