"""Tests for vigia.ui.jobs — job state machine, log offsets, concurrency,
timeout, and the three-fact verdict panel (exit code / label / sealed bundle),
using a fake agent script instead of the real vigia_agent.py."""

import json
import time

import pytest

from vigia.ui.bundle_index import BundleIndex
from vigia.ui.jobs import JobBusyError, JobRunner, JobValidationError

FAKE_AGENT = r'''
import argparse, json, sys, time, os

p = argparse.ArgumentParser()
p.add_argument("--evidence", required=True)
p.add_argument("--case-id", required=True)
p.add_argument("--output", default=None)
p.add_argument("--examiner-id", default=None)
p.add_argument("--acquisition-tool", default=None)
p.add_argument("--write-blocker-used", default=None)
args = p.parse_args()

mode = os.environ.get("FAKE_AGENT_MODE", "suspicion")
print("[fake-agent] start", args.case_id, flush=True)
if mode == "slow":
    time.sleep(60)
if mode == "crash":
    print("[fake-agent] boom", flush=True)
    sys.exit(2)
verdict = {"suspicion": "SUSPICION", "disagree": "MALICE"}[mode]
bundle = {
    "case_id": args.case_id,
    "agent_verdict": verdict,
    "analysis_timestamp": "2026-01-01T00:00:00Z",
    "audit_trail": {"total_entries": 0, "entries": []},
    "pipeline_results": {"abduction": {}, "signals": []},
}
with open(args.output, "w") as fh:
    json.dump(bundle, fh)
print("[fake-agent] sealed", flush=True)
# exit code deliberately disagrees with the bundle in "disagree" mode
sys.exit(5 if mode == "suspicion" else 3)
'''


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "cases").mkdir(parents=True)
    (root / "cases" / "ev.json").write_text('{"artifacts": []}')
    (root / "results").mkdir()
    (root / "fake_agent.py").write_text(FAKE_AGENT)
    return root


def make_runner(repo, timeout_s=30):
    idx = BundleIndex(repo)
    idx.refresh()
    return JobRunner(repo, bundle_index=idx,
                     agent_script=repo / "fake_agent.py",
                     max_jobs=1, timeout_s=timeout_s)


def wait_done(runner, job_id, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = runner.get(job_id)
        if job["state"] in ("done", "error"):
            return job
        time.sleep(0.05)
    pytest.fail("job did not finish in time")


def test_happy_path_verdict_triple(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "suspicion")
    runner = make_runner(repo)
    job_id = runner.submit("cases/ev.json", "T-001")
    job = wait_done(runner, job_id)
    assert job["state"] == "done"
    assert job["exit_code"] == 5
    assert job["exit_code_verdict"] == "SUSPICION"
    assert job["verdict_from_bundle"] == "SUSPICION"
    assert job["verdicts_agree"] is True
    assert job["bundle_id"] is not None
    assert job["output_bundle_rel_path"].startswith("results/webui/T-001_")
    # sealed bundle registered in the index
    entry = runner.bundle_index.get(job["bundle_id"])
    assert entry["case_id"] == "T-001"


def test_disagreement_surfaced_not_reconciled(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "disagree")
    runner = make_runner(repo)
    job = wait_done(runner, runner.submit("cases/ev.json", "T-002"))
    assert job["exit_code_verdict"] == "INTENT"       # exit 3
    assert job["verdict_from_bundle"] == "MALICE"     # sealed bundle
    assert job["verdicts_agree"] is False


def test_crash_no_bundle(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "crash")
    runner = make_runner(repo)
    job = wait_done(runner, runner.submit("cases/ev.json", "T-003"))
    assert job["exit_code"] == 2
    assert job["exit_code_verdict"] == "ERROR"
    assert job["verdict_from_bundle"] is None
    assert job["verdicts_agree"] is None


def test_log_offsets_and_polling(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "suspicion")
    runner = make_runner(repo)
    job_id = runner.submit("cases/ev.json", "T-004")
    wait_done(runner, job_id)
    full = runner.read_log(job_id, 0)
    assert any("[fake-agent] sealed" in l for l in full["lines"])
    assert full["truncated"] is False
    # incremental poll from the end sees nothing new
    tail = runner.read_log(job_id, full["next_offset"])
    assert tail["lines"] == []
    assert runner.read_log("nope", 0) is None


def test_concurrency_slot_busy(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "slow")
    runner = make_runner(repo, timeout_s=30)
    first = runner.submit("cases/ev.json", "T-005")
    time.sleep(0.2)
    with pytest.raises(JobBusyError):
        runner.submit("cases/ev.json", "T-006")
    runner.shutdown()
    job = wait_done(runner, first)
    assert job["state"] == "error"  # terminated by shutdown


def test_timeout_kills_process(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "slow")
    runner = make_runner(repo, timeout_s=1)
    job = wait_done(runner, runner.submit("cases/ev.json", "T-007"), timeout=25)
    assert job["state"] == "error"
    assert "timeout" in (job["error"] or "")


def test_validation_rejections(repo):
    runner = make_runner(repo)
    with pytest.raises(JobValidationError):
        runner.submit("cases/ev.json", "bad id with spaces")
    with pytest.raises(JobValidationError):
        runner.submit("cases/ev.json", "-leadingdash")
    with pytest.raises(JobValidationError):
        runner.submit("../etc/passwd", "T-008")
    with pytest.raises(JobValidationError):
        runner.submit("/etc/passwd", "T-009")
    with pytest.raises(JobValidationError):
        runner.submit("cases/missing.json", "T-010")


def test_rerun_never_overwrites_previous_bundle(repo, monkeypatch):
    monkeypatch.setenv("FAKE_AGENT_MODE", "suspicion")
    runner = make_runner(repo)
    j1 = wait_done(runner, runner.submit("cases/ev.json", "T-011"))
    j2 = wait_done(runner, runner.submit("cases/ev.json", "T-011"))
    assert j1["output_bundle_rel_path"] != j2["output_bundle_rel_path"]
    assert (repo / j1["output_bundle_rel_path"]).is_file()
    assert (repo / j2["output_bundle_rel_path"]).is_file()
