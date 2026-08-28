"""Tests for vigia.ui.bundle_index — scan, sidecar/trace association, opaque
ids, honest listing of unparseable files, cache refresh."""

import json
import time

from vigia.ui.bundle_index import BundleIndex, bundle_id_for


def write_json(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    write_json(repo / "results" / "a_bundle.json", {
        "case_id": "CASE-A", "agent_verdict": "NOISE",
        "analysis_timestamp": "2026-01-01T00:00:00Z",
        "audit_trail": {"total_entries": 0, "entries": []},
        "pipeline_results": {"abduction": {}, "signals": []},
    })
    write_json(repo / "results" / "sub" / "b_bundle.json", {
        "case_id": "CASE-B", "overall_verdict": "MALICE",
        "analysis_timestamp": "2026-02-01T00:00:00Z",
        "findings": [], "tool_execution_log": [],
    })
    # sidecar + reasoning trace for a_bundle
    (repo / "results" / "a_bundle.json.sha256").write_text("ff" * 32 + "  x\n")
    write_json(repo / "results" / "a_bundle_reasoning_trace.json", {"steps": []})
    # unparseable file
    (repo / "cases").mkdir(parents=True)
    (repo / "cases" / "broken.json").write_text("{not json", encoding="utf-8")
    return repo


def test_scan_and_classify(tmp_path):
    idx = BundleIndex(make_repo(tmp_path))
    idx.refresh()
    assert len(idx) == 3  # trace file not indexed as a bundle
    counts = idx.counts_by_schema()
    assert counts == {"agent_audit": 1, "mcp_investigation": 1, "unparseable": 1}


def test_sidecar_and_trace_association(tmp_path):
    idx = BundleIndex(make_repo(tmp_path))
    idx.refresh()
    entry = idx.get(bundle_id_for("results/a_bundle.json"))
    assert entry["has_sha256_sidecar"] is True
    assert entry["has_reasoning_trace"] is True
    other = idx.get(bundle_id_for("results/sub/b_bundle.json"))
    assert other["has_sha256_sidecar"] is False
    assert other["has_reasoning_trace"] is False


def test_opaque_id_stability(tmp_path):
    repo = make_repo(tmp_path)
    idx = BundleIndex(repo)
    idx.refresh()
    id1 = bundle_id_for("results/a_bundle.json")
    assert idx.get(id1)["case_id"] == "CASE-A"
    # id derives only from rel_path — stable across rescans
    idx.refresh(force=True)
    assert idx.get(id1)["case_id"] == "CASE-A"


def test_unparseable_listed_honestly(tmp_path):
    idx = BundleIndex(make_repo(tmp_path))
    idx.refresh()
    entry = idx.get(bundle_id_for("cases/broken.json"))
    assert entry is not None
    assert entry["schema"] == "unparseable"
    assert entry["verdicts"] == []


def test_query_filters(tmp_path):
    idx = BundleIndex(make_repo(tmp_path))
    idx.refresh()
    assert idx.query(verdict="MALICE")["total"] == 1
    assert idx.query(schema="agent_audit")["total"] == 1
    assert idx.query(case="case-a")["total"] == 1
    assert idx.query(q="sub/")["total"] == 1
    page = idx.query(limit=1, offset=0)
    assert page["total"] == 3 and len(page["items"]) == 1
    # abs_path never leaks over the query surface
    assert all("abs_path" not in item for item in page["items"])


def test_refresh_picks_up_changes_and_deletions(tmp_path):
    repo = make_repo(tmp_path)
    idx = BundleIndex(repo)
    idx.refresh()
    target = repo / "results" / "a_bundle.json"
    doc = json.loads(target.read_text())
    doc["agent_verdict"] = "MALICE"
    time.sleep(0.01)  # ensure mtime moves
    target.write_text(json.dumps(doc))
    idx.refresh()
    entry = idx.get(bundle_id_for("results/a_bundle.json"))
    assert entry["verdicts"][0]["verdict"] == "MALICE"

    target.unlink()
    idx.refresh()
    assert idx.get(bundle_id_for("results/a_bundle.json")) is None


def test_register_file_confined_to_repo(tmp_path):
    repo = make_repo(tmp_path)
    idx = BundleIndex(repo)
    idx.refresh()
    outside = tmp_path / "outside.json"
    write_json(outside, {"case_id": "X"})
    assert idx.register_file(outside) is None

    new = repo / "results" / "webui" / "new_bundle.json"
    write_json(new, {
        "case_id": "CASE-NEW", "agent_verdict": "ABSTAIN",
        "audit_trail": {"total_entries": 0, "entries": []},
    })
    entry = idx.register_file(new)
    assert entry["schema"] == "agent_audit"
    assert idx.get(entry["id"])["case_id"] == "CASE-NEW"
