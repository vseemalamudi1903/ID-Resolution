import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import os

from sqlalchemy.pool import StaticPool

# Use an in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True, scope="function")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_full_customer_journey():
    # 1. Anonymous visitor browsing 'Electronics'
    response = client.post("/track", json={
        "identifiers": [{"type": "cookie_id", "value": "cookie_123"}],
        "traits": [{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "fp_123"}],
        "event": {"event_type": "page_view", "category": "Electronics"}
    })
    assert response.status_code == 200
    data = response.json()
    canonical_id_1 = data["canonical_id"]
    assert len(data["interest_scores"]) == 1
    assert data["interest_scores"][0]["category"] == "Electronics"
    assert data["interest_scores"][0]["score"] == 1.0

    # 2. Same visitor logs in with email (Partial Knowledge)
    response = client.post("/track", json={
        "identifiers": [
            {"type": "cookie_id", "value": "cookie_123"},
            {"type": "email", "value": "john@example.com"}
        ],
        "traits": [{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "fp_123"}],
        "event": {"event_type": "product_view", "category": "Electronics"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == canonical_id_1
    # Score should be 1.0 (prev) + 2.0 (product_view) = 3.0
    scores = {s["category"]: s["score"] for s in data["interest_scores"]}
    assert scores["Electronics"] == 3.0
    assert any(id["type"] == "email" and id["value"] == "john@example.com" for id in data["identifiers"])

    # 3. Same visitor becomes a Loyalty Member
    response = client.post("/track", json={
        "identifiers": [
            {"type": "email", "value": "john@example.com"},
            {"type": "loyalty_id", "value": "L_999"}
        ],
        "traits": [{"type": "ip", "value": "1.1.1.1"}, {"type": "fingerprint", "value": "fp_123"}],
        "event": {"event_type": "purchase", "category": "Electronics"}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["canonical_id"] == canonical_id_1
    scores = {s["category"]: s["score"] for s in data["interest_scores"]}
    # 3.0 (prev) + 5.0 (purchase) = 8.0
    assert scores["Electronics"] == 8.0
    assert any(id["type"] == "loyalty_id" and id["value"] == "L_999" for id in data["identifiers"])

def test_probabilistic_merge():
    # 1. Device A browsing
    client.post("/track", json={
        "identifiers": [{"type": "cookie_id", "value": "cookie_A"}],
        "traits": [{"type": "ip", "value": "2.2.2.2"}, {"type": "fingerprint", "value": "fp_456"}],
        "event": {"event_type": "page_view", "category": "Fashion"}
    })

    # 2. Device B browsing (Different cookie but same IP + Fingerprint)
    response = client.post("/track", json={
        "identifiers": [{"type": "cookie_id", "value": "cookie_B"}],
        "traits": [{"type": "ip", "value": "2.2.2.2"}, {"type": "fingerprint", "value": "fp_456"}],
        "event": {"event_type": "page_view", "category": "Fashion"}
    })

    assert response.status_code == 200
    data = response.json()
    # Should have both cookies now
    ids = [id["value"] for id in data["identifiers"]]
    assert "cookie_A" in ids
    assert "cookie_B" in ids
    # Score should be 1.0 + 1.0 = 2.0
    scores = {s["category"]: s["score"] for s in data["interest_scores"]}
    assert scores["Fashion"] == 2.0

def test_deterministic_merge_separate_profiles():
    # 1. Profile 1 with Email
    resp1 = client.post("/track", json={
        "identifiers": [{"type": "email", "value": "merge@test.com"}],
        "event": {"event_type": "page_view", "category": "Home"}
    })
    can_id_1 = resp1.json()["canonical_id"]

    # 2. Profile 2 with Cookie
    resp2 = client.post("/track", json={
        "identifiers": [{"type": "cookie_id", "value": "cookie_merge"}],
        "event": {"event_type": "page_view", "category": "Garden"}
    })
    can_id_2 = resp2.json()["canonical_id"]
    assert can_id_1 != can_id_2

    # 3. Track event with BOTH Email and Cookie -> Should merge
    resp3 = client.post("/track", json={
        "identifiers": [
            {"type": "email", "value": "merge@test.com"},
            {"type": "cookie_id", "value": "cookie_merge"}
        ],
        "event": {"event_type": "page_view", "category": "Home"}
    })

    data = resp3.json()
    # One of them should have been deleted, result should be unified
    # Check that both categories exist in interest scores
    scores = {s["category"]: s["score"] for s in data["interest_scores"]}
    assert "Home" in scores
    assert "Garden" in scores
    assert scores["Home"] == 2.0 # 1.0 from resp1 + 1.0 from resp3
    assert scores["Garden"] == 1.0 # from resp2
