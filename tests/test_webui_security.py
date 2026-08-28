"""Security tests for the web UI: evidence confinement (traversal, absolute
paths, symlinks, foreign roots), case-id injection, and cross-site POST
rejection at the HTTP layer."""

import json
import os

import pytest
from fastapi.testclient import TestClient

from vigia.ui.evidence_paths import (
    EvidencePathError,
    list_evidence_roots,
    resolve_evidence_path,
)
from vigia.ui.server import create_app


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "cases").mkdir(parents=True)
    (root / "cases" / "ev.json").write_text("{}")
    (root / "cases" / "evdir").mkdir()
    (root / "evidence").mkdir()
    (root / "results").mkdir()
    (root / "secret.txt").write_text("outside")
    return root


# ---------------------------------------------------------------------------
# evidence path confinement
# ---------------------------------------------------------------------------

def test_valid_file_and_dir(repo):
    assert resolve_evidence_path(repo, "cases/ev.json").name == "ev.json"
    assert resolve_evidence_path(repo, "cases/evdir").is_dir()


@pytest.mark.parametrize("bad", [
    "../etc/passwd",
    "cases/../secret.txt",
    "/etc/passwd",
    "secret.txt",                 # outside declared roots
    "results/x.json",             # results/ root itself is not allowlisted
    "cases",                      # the bare root is not a target
    "",
])
def test_confinement_rejections(repo, bad):
    with pytest.raises(EvidencePathError):
        resolve_evidence_path(repo, bad)


def test_symlink_component_rejected(repo, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "data.json").write_text("{}")
    link = repo / "cases" / "link"
    os.symlink(outside, link)
    with pytest.raises(EvidencePathError):
        resolve_evidence_path(repo, "cases/link/data.json")
    # symlink leaf equally rejected
    leaf = repo / "cases" / "leaf.json"
    os.symlink(outside / "data.json", leaf)
    with pytest.raises(EvidencePathError):
        resolve_evidence_path(repo, "cases/leaf.json")


def test_list_roots_omits_symlinks(repo, tmp_path):
    outside = tmp_path / "outside2"
    outside.mkdir()
    os.symlink(outside, repo / "cases" / "sneaky")
    roots = list_evidence_roots(repo)
    cases = [r for r in roots["roots"] if r["root"] == "cases"][0]
    names = [e["rel_path"] for e in cases["entries"]]
    assert "sneaky" not in names
    assert "ev.json" in names


# ---------------------------------------------------------------------------
# HTTP layer
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(repo):
    return TestClient(create_app(repo_root=repo))


def test_investigation_traversal_422(client):
    res = client.post("/api/investigations",
                      json={"evidence_path": "../etc/passwd", "case_id": "T-1"})
    assert res.status_code == 422


def test_investigation_case_id_injection_422(client):
    for bad in ("T 1; rm -rf /", "--output", "-x", "a/../b", "á-ñ"):
        res = client.post("/api/investigations",
                          json={"evidence_path": "cases/ev.json", "case_id": bad})
        assert res.status_code == 422, bad


def test_investigation_cross_site_origin_403(client):
    res = client.post("/api/investigations",
                      json={"evidence_path": "cases/ev.json", "case_id": "T-1"},
                      headers={"Origin": "https://attacker.example"})
    assert res.status_code == 403


def test_investigation_cross_site_referer_403(client):
    res = client.post("/api/investigations",
                      json={"evidence_path": "cases/ev.json", "case_id": "T-1"},
                      headers={"Referer": "https://attacker.example/page"})
    assert res.status_code == 403


def test_unknown_job_404(client):
    assert client.get("/api/investigations/nope").status_code == 404
    assert client.get("/api/investigations/nope/log").status_code == 404


def test_evidence_listing_shape(client):
    body = client.get("/api/evidence").json()
    roots = {r["root"] for r in body["roots"]}
    assert "cases" in roots and "evidence" in roots
