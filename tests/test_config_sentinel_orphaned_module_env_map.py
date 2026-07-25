"""
vigia/core/config_sentinel.py -- addendum to B-124 (Verdict/governance
cluster: 6 modules designed, not wired), found while continuing that
excavation in the "Round 2" audit spirit (B-217..B-222).

ConfigAuditMonitor's stated purpose is detecting when a CRITICAL_MODULES
entry (CAIE, TrustFusion, OckhamAdversarial, SignalRouter) is disabled, via
_MODULE_ENV_MAP mapping each module name to an env var the monitor reads.
Of the 9 total mapped variables (4 critical + 5 important), only
VIGIA_CAIE_ENABLED and VIGIA_TRUST_FUSION_ENABLED are read anywhere else in
this repository -- confirmed by exhaustive grep. The other 7, including both
remaining CRITICAL_MODULES entries (VIGIA_OCKHAM_ADVERSARIAL,
VIGIA_SIGNALROUTER_ENABLED), gate nothing: ockham_adversarial.py has zero
callers (see the B-124 adversarial_penalty addendum) and
advanced_signal_router.py is conceptually superseded per B-124's own text.

_getenv_bool defaults an unset variable to "active" -- correct if the
variable genuinely controlled the module, but backwards here: it makes
ConfigAuditMonitor report OckhamAdversarial and SignalRouter as active
(FULL_INTEGRITY, no analyst_warning) precisely when they are, in fact,
entirely disconnected from the live pipeline. This is not merely "not wired"
-- if config_sentinel were wired into the pipeline today without first
fixing _MODULE_ENV_MAP, it would seal a sentinel report with a false
integrity guarantee for exactly the two modules already known to be broken.

This test locks in that behavior so a future partial fix (wiring
config_sentinel without repairing the map) is caught here rather than
shipping a monitor that lies about its own subject.
"""

from __future__ import annotations


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
                f"{readers} -- the orphaned-module premise of the B-124 "
                f"addendum may no longer hold, review it."
            )


class TestConfigAuditMonitorFalselyReportsOrphanedCriticalModulesAsActive:
    def test_clean_environment_reports_full_integrity(self, monkeypatch):
        for var in (
            "VIGIA_CAIE_ENABLED", "VIGIA_TRUST_FUSION_ENABLED",
            "VIGIA_OCKHAM_ADVERSARIAL", "VIGIA_SIGNALROUTER_ENABLED",
            "VIGIA_PDF_ENABLED", "VIGIA_NETWORK_ENABLED",
            "VIGIA_REGISTRY_ENABLED", "VIGIA_EMAIL_ENABLED",
            "VIGIA_TEMPORAL_ENABLED",
        ):
            monkeypatch.delenv(var, raising=False)

        from vigia.core.config_sentinel import ConfigAuditMonitor

        mon = ConfigAuditMonitor(secret_key=b"test-key")
        mon.initialize()
        trail = mon.finalize()
        report = trail.to_report_dict()

        assert report["integrity_level"] == "FULL_INTEGRITY"
        assert report["analyst_warning"] is None

    def test_ockham_and_signalrouter_report_active_despite_having_no_real_gate(
        self, monkeypatch
    ):
        """The core finding: these two CRITICAL_MODULES entries are reported
        active=True by a monitor whose own sibling module (ockham_adversarial.py,
        advanced_signal_router.py) has no live path that could ever set the
        env vars this check depends on -- the "active" signal is meaningless,
        not reassuring."""
        for var in ("VIGIA_OCKHAM_ADVERSARIAL", "VIGIA_SIGNALROUTER_ENABLED"):
            monkeypatch.delenv(var, raising=False)

        from vigia.core.config_sentinel import ConfigAuditMonitor

        mon = ConfigAuditMonitor(secret_key=b"test-key")
        mon.initialize()
        trail = mon.finalize()

        by_name = {s.name: s for s in trail.module_snapshots}
        assert by_name["OckhamAdversarial"].active is True
        assert by_name["OckhamAdversarial"].env_value == "NOT_SET"
        assert by_name["SignalRouter"].active is True
        assert by_name["SignalRouter"].env_value == "NOT_SET"
