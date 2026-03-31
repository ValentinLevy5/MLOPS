from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PARAMS = {
    "price": 300000,
    "surface": 60,
    "rooms": 3,
    "latitude": 48.71,
    "longitude": 2.16,
}


def test_root():
    r = client.get("/")
    assert r.status_code == 200


def test_score_valid():
    r = client.get("/score", params=VALID_PARAMS)
    assert r.status_code == 200
    data = r.json()
    assert "final_score" in data
    assert 0 <= data["final_score"] <= 1


def test_score_missing_field():
    params = {k: v for k, v in VALID_PARAMS.items() if k != "latitude"}
    assert client.get("/score", params=params).status_code == 422


def test_score_invalid_latitude():
    assert client.get("/score", params={**VALID_PARAMS, "latitude": 200}).status_code == 422


def test_score_negative_price():
    assert client.get("/score", params={**VALID_PARAMS, "price": -100}).status_code == 422
