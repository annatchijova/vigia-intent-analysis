"""Tests for vigia.ui.verify — subprocess wrappers (mocked) and the pure
sidecar check. The real verifiers are exercised end-to-end against the
corpus manually; here we pin the wrapper contract."""

import hashlib
import json
import subprocess

from vigia.ui import verify


def _completed(returncode, stdout="", stderr=""):
    return subprocess.CompletedProcess(args=[], returncode=returncode,
                                       stdout=stdout, stderr=stderr)


def test_ebs_v1_pass_parses_json(monkeypatch, tmp_path):
    (tmp_path / "forensics").mkdir()
    (tmp_path / "forensics" / "verify_ebs_v1.py").write_text("# stub")
    payload = {"passed": True, "conformity_level": 3,
               "conformity_label": "Fully compliant EBS v1",
               "checks": [{"rule": "R1", "passed": True, "message": "ok"}]}
    monkeypatch.setattr(verify, "_run",
                        lambda cmd, cwd: _completed(0, json.dumps(payload)))
    r = verify.run_ebs_v1(tmp_path, tmp_path / "b.json")
    assert r["status"] == "PASS" and r["exit_code"] == 0
    assert r["conformity_level"] == 3
    assert r["checks"][0]["rule"] == "R1"


def test_ebs_v1_fail_keeps_exit_code(monkeypatch, tmp_path):
    (tmp_path / "forensics").mkdir()
    (tmp_path / "forensics" / "verify_ebs_v1.py").write_text("# stub")
    monkeypatch.setattr(verify, "_run",
                        lambda cmd, cwd: _completed(1, json.dumps({"passed": False})))
    r = verify.run_ebs_v1(tmp_path, tmp_path / "b.json")
    assert r["status"] == "FAIL" and r["exit_code"] == 1


def test_ebs_v1_missing_verifier(tmp_path):
    r = verify.run_ebs_v1(tmp_path, tmp_path / "b.json")
    assert r["status"] == "ERROR"


def test_tool_log_exit_code_map(monkeypatch, tmp_path):
    (tmp_path / "verify_tool_log.py").write_text("# stub")
    for code, status in ((0, "VERIFIED"), (1, "BROKEN"), (2, "NO_LOG"),
                         (3, "ERROR")):
        monkeypatch.setattr(verify, "_run",
                            lambda cmd, cwd, c=code: _completed(c, "out"))
        r = verify.run_tool_log(tmp_path, tmp_path / "b.json")
        assert r["status"] == status, code


def test_tool_log_hmac_key_in_argv_not_in_response(monkeypatch, tmp_path):
    (tmp_path / "verify_tool_log.py").write_text("# stub")
    seen = {}

    def fake_run(cmd, cwd):
        seen["cmd"] = cmd
        return _completed(0, "VERIFIED")

    monkeypatch.setattr(verify, "_run", fake_run)
    r = verify.run_tool_log(tmp_path, tmp_path / "b.json", hmac_key_hex="deadbeef")
    assert "--hmac-key-hex" in seen["cmd"]
    assert "deadbeef" not in json.dumps({k: v for k, v in r.items()})


def test_sidecar_match_and_mismatch(tmp_path):
    bundle = tmp_path / "x_bundle.json"
    bundle.write_text('{"a": 1}')
    digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    sidecar = tmp_path / "x_bundle.json.sha256"

    sidecar.write_text(f"{digest}  {bundle}\n")
    assert verify.check_sidecar(bundle)["status"] == "MATCH"

    sidecar.write_text("0" * 64 + f"  {bundle}\n")
    assert verify.check_sidecar(bundle)["status"] == "MISMATCH"


def test_sidecar_absent_and_malformed(tmp_path):
    bundle = tmp_path / "y_bundle.json"
    bundle.write_text("{}")
    assert verify.check_sidecar(bundle)["status"] == "ABSENT"
    (tmp_path / "y_bundle.json.sha256").write_text("not-a-hash\n")
    assert verify.check_sidecar(bundle)["status"] == "ERROR"
