"""Tests for the vigia.ui.server read-side endpoints (health, bundles, raw)
and the cross-site write guard."""

import json

import pytest
from fastapi.testclient import TestClient

from vigia.ui.bundle_index import bundle_id_for
from vigia.ui.server import create_app


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "results").mkdir(parents=True)
    (root / "results" / "a_bundle.json").write_text(json.dumps({
        "case_id": "CASE-A", "agent_verdict": "SUSPICION",
        "analysis_timestamp": "2026-01-01T00:00:00Z",
        "audit_trail": {"total_entries": 1, "entries": [
            {"seq": 1, "timestamp": "t", "action": "SESSION_START",
             "tool": "vigia_agent", "note": "n"}]},
        "pipeline_results": {"abduction": {}, "signals": [
            {"artifact_id": "ART-001", "description": "sig",
             "confidence": {"__fraction__": True, "num": 1, "den": 3}}]},
    }))
    (root / "results" / "big.json").write_text(
        json.dumps({"case_id": "BIG", "overall_verdict": "NOISE",
                    "findings": [], "pad": "x" * (11 * 1024 * 1024)}))
    return root


@pytest.fixture()
def client(repo):
    return TestClient(create_app(repo_root=repo))


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["bundle_count"] == 2
    assert "agent_audit" in body["schemas"]


def test_list_and_filter(client):
    body = client.get("/api/bundles").json()
    assert body["total"] == 2
    body = client.get("/api/bundles", params={"verdict": "SUSPICION"}).json()
    assert body["total"] == 1
    assert body["items"][0]["case_id"] == "CASE-A"
    assert all("abs_path" not in i for i in body["items"])


def test_detail_normalized(client):
    bid = bundle_id_for("results/a_bundle.json")
    body = client.get(f"/api/bundles/{bid}").json()
    assert body["schema"] == "agent_audit"
    assert body["verdicts"][0]["verdict"] == "SUSPICION"
    assert body["findings"][0]["confidence"] == "1/3"
    assert body["sidecar"] == {"has_sha256_sidecar": False,
                               "has_reasoning_trace": False}


def test_detail_unknown_id_404(client):
    assert client.get("/api/bundles/deadbeefdeadbeef").status_code == 404


def test_raw_roundtrip_preserves_fractions(client):
    bid = bundle_id_for("results/a_bundle.json")
    res = client.get(f"/api/bundles/{bid}/raw")
    assert res.status_code == 200
    doc = res.json()
    frac = doc["pipeline_results"]["signals"][0]["confidence"]
    assert frac == {"__fraction__": True, "num": 1, "den": 3}


def test_raw_cap_413(client):
    bid = bundle_id_for("results/big.json")
    assert client.get(f"/api/bundles/{bid}/raw").status_code == 413


def test_cross_site_post_rejected(client):
    bid = bundle_id_for("results/a_bundle.json")
    res = client.post(f"/api/bundles/{bid}/verify",
                      json={"verifier": "sidecar"},
                      headers={"Origin": "https://evil.example"})
    assert res.status_code == 403


def test_non_json_post_rejected(client):
    bid = bundle_id_for("results/a_bundle.json")
    res = client.post(f"/api/bundles/{bid}/verify",
                      content="verifier=sidecar",
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert res.status_code == 415


def test_local_origin_post_allowed(client):
    bid = bundle_id_for("results/a_bundle.json")
    res = client.post(f"/api/bundles/{bid}/verify",
                      json={"verifier": "sidecar"},
                      headers={"Origin": "http://127.0.0.1:8010"})
    assert res.status_code == 200
    assert res.json()["status"] == "ABSENT"  # no sidecar in the fixture


def test_spa_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "VIGÍA" in res.text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/i18n.js").status_code == 200
    # i18n must load before the app so t() finds the tables
    assert res.text.index("/static/i18n.js") < res.text.index("/static/app.js")


def test_i18n_tables_have_identical_keys():
    """EN and ES chrome tables must cover exactly the same keys — a missing
    translation would silently fall back and go unnoticed."""
    import re
    from pathlib import Path

    src = (Path(__file__).parent.parent / "vigia" / "ui" / "static"
           / "i18n.js").read_text(encoding="utf-8")
    sections = re.split(r"^\s{2}(en|es): \{", src, flags=re.M)
    tables = {}
    for name, body in zip(sections[1::2], sections[2::2]):
        tables[name] = set(re.findall(r'^\s{4}"([a-z0-9_.]+)":', body, flags=re.M))
    assert set(tables) == {"en", "es"}
    assert tables["en"], "no keys extracted — regex out of sync with i18n.js"
    assert tables["en"] == tables["es"], (
        f"only in en: {sorted(tables['en'] - tables['es'])}; "
        f"only in es: {sorted(tables['es'] - tables['en'])}"
    )
