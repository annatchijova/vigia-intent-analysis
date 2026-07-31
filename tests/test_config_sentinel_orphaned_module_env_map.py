"""
vigia/core/config_sentinel.py -- B-124 addendum, now FIXED (Claude 2026-07-31).

ConfigAuditMonitor's stated purpose is detecting when a CRITICAL_MODULES entry
(CAIE, TrustFusion, OckhamAdversarial, SignalRouter) is disabled, via
_MODULE_ENV_MAP mapping each module name to an env var the monitor reads. Of the
9 mapped variables, only VIGIA_CAIE_ENABLED and VIGIA_TRUST_FUSION_ENABLED are
read anywhere else in the repository (confirmed by exhaustive grep). The other 7,
including both remaining CRITICAL_MODULES entries (VIGIA_OCKHAM_ADVERSARIAL,
VIGIA_SIGNALROUTER_ENABLED), gate nothing: ockham_adversarial.py and
advanced_signal_router.py have zero production callers.

Previously `_getenv_bool` defaulted an unset variable to "active", so the
monitor reported OckhamAdversarial and SignalRouter as active (FULL_INTEGRITY,
no analyst_warning) precisely when they were entirely disconnected — a sealed
integrity report that would lie about its own subject.

Fix: `_UNWIRED_MODULES` marks the two orphaned criticals as NOT WIRED; the
monitor reports them active=False, seals DEGRADED_MODE with an analyst_warning,
and no longer manufactures an "active" signal from an env-var default nobody
reads. When either module is genuinely wired, its name is removed from
`_UNWIRED_MODULES` in the same commit and the monitor returns to FULL on its own.

This file was a characterization test locking in the lie; it is now a guard
that the lie stays fixed (and that CAIE/TrustFusion, which have real gates, are
untouched).
"""

from __future__ import annotations

import pytest


_ALL_MAPPED_VARS = (
    "VIGIA_CAIE_ENABLED", "VIGIA_TRUST_FUSION_ENABLED",
    "VIGIA_OCKHAM_ADVERSARIAL", "VIGIA_SIGNALROUTER_ENABLED",
    "VIGIA_PDF_ENABLED", "VIGIA_NETWORK_ENABLED",
    "VIGIA_REGISTRY_ENABLED", "VIGIA_EMAIL_ENABLED",
    "VIGIA_TEMPORAL_ENABLED",
)


class TestOrphanedModuleEnvVarsAreNeverReadElsewhere:
    def test_ockham_and_signalrouter_env_vars_have_no_other_reader(self):
        import subprocess

        repo_root = __file__.rsplit("/tests/", 1)[0]
        for var in ("VIGIA_OCKHAM_ADVERSARIAL", "VIGIA_SIGNALROUTER_ENABLED"):
            result = subprocess.run(
                ["grep", "-rl", var, "--include=*.py", "."],
                cwd=repo_root, capture_output=True, text=True,
            )
            readers = [
                line for line in result.stdout.splitlines()
                if "vigia/core/config_sentinel.py" not in line
                and "test_config_sentinel_orphaned_module_env_map.py" not in line
            ]
            assert readers == [], (
                f"{var} now has a reader outside config_sentinel.py: "
                f"{readers} -- the orphaned-module premise may no longer hold. "
                f"If the module is now wired, drop it from _UNWIRED_MODULES."
            )


class TestConfigAuditMonitorTellsTheTruthAboutOrphanedCriticalModules:
    @pytest.fixture
    def clean_env(self, monkeypatch):
        for var in _ALL_MAPPED_VARS:
            monkeypatch.delenv(var, raising=False)

    def _finalize(self):
        from vigia.core.config_sentinel import ConfigAuditMonitor
        mon = ConfigAuditMonitor(secret_key=b"test-key")
        mon.initialize()
        return mon.finalize()

    def test_clean_environment_reports_degraded_not_full(self, clean_env):
        report = self._finalize().to_report_dict()
        assert report["integrity_level"] == "DEGRADED_MODE"
        assert report["analyst_warning"] is not None
        assert "OckhamAdversarial" in report["analyst_warning"]
        assert "SignalRouter" in report["analyst_warning"]
        assert report["critical_modules_inactive_at_init"] == [
            "OckhamAdversarial", "SignalRouter",
        ]

    def test_orphaned_criticals_report_inactive_and_not_wired(self, clean_env):
        by_name = {s.name: s for s in self._finalize().module_snapshots}
        for m in ("OckhamAdversarial", "SignalRouter"):
            assert by_name[m].active is False
            assert by_name[m].env_value == "NOT_WIRED"

    def test_really_wired_criticals_stay_active(self, clean_env):
        # CAIE and TrustFusion have real env gates (5 and 4 readers) and must
        # NOT be swept up by the unwired-module handling.
        by_name = {s.name: s for s in self._finalize().module_snapshots}
        assert by_name["CAIE"].active is True
        assert by_name["TrustFusion"].active is True

    def test_runtime_deactivation_of_a_real_critical_still_detected(self, clean_env, monkeypatch):
        # The genuine deactivation path (CAIE disabled) must still degrade —
        # the fix must not blunt real detection.
        monkeypatch.setenv("VIGIA_CAIE_ENABLED", "false")
        by_name = {s.name: s for s in self._finalize().module_snapshots}
        assert by_name["CAIE"].active is False
        report = self._finalize().to_report_dict()
        assert report["integrity_level"] == "DEGRADED_MODE"
        assert "CAIE" in report["analyst_warning"]
