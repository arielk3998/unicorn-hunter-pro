import os
from jose import jwt
from fastapi.testclient import TestClient
from app.presentation.api.main import create_app


def test_api_key_rejection(monkeypatch):
    monkeypatch.setenv("API_KEY", "expected-key")
    client = TestClient(create_app())
    r = client.get("/health", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401
    r2 = client.get("/health", headers={"X-API-Key": "expected-key"})
    assert r2.status_code == 200


def test_jwt_auth_allows_without_api_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET", "testsecret")
    token = jwt.encode({"sub": "user1"}, "testsecret", algorithm="HS256")
    client = TestClient(create_app())
    r = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_jwt_or_api_key_either(monkeypatch):
    monkeypatch.setenv("API_KEY", "key123")
    monkeypatch.setenv("JWT_SECRET", "secret123")
    token = jwt.encode({"sub": "user2"}, "secret123", algorithm="HS256")
    client = TestClient(create_app())
    # Missing both -> 401
    r = client.get("/health")
    assert r.status_code == 401
    # API key alone succeeds
    r2 = client.get("/health", headers={"X-API-Key": "key123"})
    assert r2.status_code == 200
    # JWT alone succeeds
    r3 = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200


def test_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RPM", "3")
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    client = TestClient(create_app())
    # First three requests succeed
    for _ in range(3):
        assert client.get("/health").status_code == 200
    # Fourth should be limited
    r = client.get("/health")
    assert r.status_code == 429