"""
Pins S3 — bordes de banda de los conversores de timestamp mobile
(AUDITORIA_COBERTURA_MOBILE_SIFT §B; WHAT_IS_NEXT §1.3.2).

Los tres conversores adivinan la unidad (ns/µs/ms/s) por MAGNITUD. Un valor
que roza un borde de banda se divide por el factor equivocado → epoch off por
~1000× → timeline forense corrompido. Estos pins fijan cada borde EXACTO
(el primer valor de cada banda y el último de la anterior) para que cualquier
refactor de umbrales — p.ej. una "unificación" entre módulos, que hoy usan
umbrales DISTINTOS a propósito (épocas WebKit vs Core Data) — dispare acá.

La división entera (sin float intermedio) quedó fijada en B-083
(tests/test_census_adjacent_fixes.py); acá se fijan las BANDAS.
"""

import pytest

from vigia.sift.android_forensics import AndroidForensicsAnalyzer
from vigia.sift.ios_forensics import iOSForensicsAnalyzer
from vigia.sift.macos_forensics import MacOSForensicsAnalyzer

_CHROME_OFFSET = 11_644_473_600   # 1601 → 1970
_COREDATA_OFFSET = 978_307_200    # 2001 → 1970


class TestChromeTsBands:
    """Android — WebKit/Chrome: >1e15 µs | >1e12 ms | >1e10 s | else raw."""

    C = staticmethod(AndroidForensicsAnalyzer._chrome_ts_to_unix)

    def test_us_band_first_value(self):
        ts = 1_000_000_000_000_001  # primer valor de la banda µs
        assert self.C(ts) == ts // 1_000_000 - _CHROME_OFFSET

    def test_us_band_edge_belongs_to_ms(self):
        ts = 1_000_000_000_000_000  # el borde EXACTO cae en ms (> estricto)
        assert self.C(ts) == ts // 1_000 - _CHROME_OFFSET

    def test_ms_band_first_value(self):
        ts = 1_000_000_000_001
        assert self.C(ts) == ts // 1_000 - _CHROME_OFFSET

    def test_ms_band_edge_belongs_to_s(self):
        ts = 1_000_000_000_000
        assert self.C(ts) == ts - _CHROME_OFFSET

    def test_s_band_first_value(self):
        ts = 10_000_000_001
        assert self.C(ts) == ts - _CHROME_OFFSET

    def test_below_s_band_returns_raw(self):
        # ≤1e10: se interpreta como unix ya convertido (passthrough).
        assert self.C(1_700_000_000) == 1_700_000_000

    def test_real_2024_microseconds(self):
        ts = 13_353_618_000_000_000  # ~2024-03 en µs WebKit
        assert self.C(ts) == 1_709_144_400

    def test_zero_negative_none(self):
        assert self.C(0) == 0
        assert self.C(-5) == 0
        assert self.C(None) == 0


class TestCoredataTsBands:
    """iOS/macOS — Core Data: >1e17 ns | >1e14 µs | >1e11 ms | else s; +offset."""

    CONVS = [iOSForensicsAnalyzer._coredata_to_unix,
             MacOSForensicsAnalyzer._coredata_to_unix]

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_ns_band_first_value(self, conv):
        ts = 100_000_000_000_000_001
        assert conv(ts) == ts // 1_000_000_000 + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_ns_edge_belongs_to_us(self, conv):
        ts = 100_000_000_000_000_000  # borde exacto → banda µs
        assert conv(ts) == ts // 1_000_000 + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_us_band_first_value(self, conv):
        ts = 100_000_000_000_001
        assert conv(ts) == ts // 1_000_000 + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_us_edge_belongs_to_ms(self, conv):
        ts = 100_000_000_000_000
        assert conv(ts) == ts // 1_000 + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_ms_band_first_value(self, conv):
        ts = 100_000_000_001
        assert conv(ts) == ts // 1_000 + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_ms_edge_belongs_to_seconds(self, conv):
        ts = 100_000_000_000
        assert conv(ts) == ts + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_seconds_band_2024(self, conv):
        ts = 730_000_000  # ~2024 en segundos Core Data
        assert conv(ts) == ts + _COREDATA_OFFSET

    @pytest.mark.parametrize("conv", CONVS, ids=["ios", "macos"])
    def test_zero_negative_none(self, conv):
        assert conv(0) == 0
        assert conv(-1) == 0
        assert conv(None) == 0

    def test_ios_and_macos_converters_agree(self):
        # Hoy son implementaciones gemelas: si divergen, que se sepa.
        for ts in (730_000_000, 100_000_000_001, 100_000_000_000_001,
                   100_000_000_000_000_001, 0, -1):
            assert (iOSForensicsAnalyzer._coredata_to_unix(ts)
                    == MacOSForensicsAnalyzer._coredata_to_unix(ts))


class TestCocoaTsFloat:
    """macOS — CFAbsoluteTime en segundos float (QuarantineEventsV2)."""

    C = staticmethod(MacOSForensicsAnalyzer._cocoa_ts_to_unix)

    def test_integer_seconds(self):
        assert self.C(730_000_000.0) == 730_000_000 + _COREDATA_OFFSET

    def test_fractional_seconds_truncate(self):
        # int() trunca hacia cero — el sub-segundo se descarta, no se redondea.
        assert self.C(730_000_000.9) == 730_000_000 + _COREDATA_OFFSET

    def test_zero_negative_none(self):
        assert self.C(0) == 0
        assert self.C(-0.5) == 0
        assert self.C(None) == 0
