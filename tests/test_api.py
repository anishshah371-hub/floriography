"""API-level tests using FastAPI's TestClient.

NOTE: these require fastapi to be installed (backend/requirements.txt)
and could NOT be executed in the sandboxed environment this project
was built in (no network access to pip-install fastapi there -- see
README.md "Known limitations"). They are written and believed correct
based on the (separately, fully-tested) service layer underneath, but
that belief is exactly the kind of claim that needs checking -- run

    cd backend && pip install -r requirements.txt
    cd .. && python -m pytest tests/test_api.py -v

and tell me what happens; this file gets fixed against real output,
not assumed correct.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_flowers():
    resp = client.get("/api/flowers")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 30
    assert len(body["results"]) == 20  # default limit


def test_list_flowers_category_filter():
    resp = client.get("/api/flowers", params={"category": "Friendship"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["results"][0]["flower"] == "Acacia"


def test_get_flower_by_id():
    resp = client.get("/api/flowers/1")
    assert resp.status_code == 200
    assert resp.json()["flower"] == "Rose, Red"


def test_get_flower_not_found():
    resp = client.get("/api/flowers/999")
    assert resp.status_code == 404


def test_flower_search_tolerant():
    for query in ["rose", "ROSE RED", "red rose"]:
        resp = client.get("/api/flowers/search", params={"query": query})
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


def test_flower_search_empty_query_rejected():
    resp = client.get("/api/flowers/search", params={"query": ""})
    assert resp.status_code == 422  # min_length=1


def test_categories_endpoint():
    resp = client.get("/api/flowers/categories")
    assert resp.status_code == 200
    assert len(resp.json()) == 12


def test_meaning_search_returns_ranked_results():
    resp = client.get("/api/search/meaning", params={"query": "I want to express friendship"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"][0]["flower"] == "Acacia"
    assert "friendship" in body["results"][0]["matched_terms"]


def test_meaning_search_no_match_returns_message_not_fabrication():
    resp = client.get("/api/search/meaning", params={"query": "zzqxxnonsensequery asdkjaslkdj"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["results"] == []
    assert body["message"]


def test_meaning_search_keyword_vs_tfidf_method():
    resp_tfidf = client.get("/api/search/meaning", params={"query": "I want to express friendship", "method": "tfidf"})
    resp_kw = client.get("/api/search/meaning", params={"query": "I want to express friendship", "method": "keyword"})
    assert resp_tfidf.json()["results"][0]["flower"] == "Acacia"
    assert resp_kw.json()["results"] == [] or resp_kw.json()["results"][0]["flower"] != "Acacia"


def test_analytics_matches_known_dataset_shape():
    resp = client.get("/api/analytics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_records"] == 30
    assert body["category_count"] == 12
    assert body["category_distribution"]["Love"] == 12
