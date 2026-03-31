from app.scoring import (
    compute_distance_score,
    compute_expected_price,
    compute_market_score,
    haversine_km,
)

MOCK_MODEL = {
    "intercept": 10.0,
    "coef_log_surface": 0.8,
    "coef_rooms": 0.1,
    "sigma": 0.3,
    "n_train": 100,
}


def test_haversine_same_point():
    assert haversine_km(48.71, 2.16, 48.71, 2.16) == 0.0


def test_haversine_paris_to_campus():
    d = haversine_km(48.8566, 2.3522, 48.7097, 2.1635)
    assert 20 < d < 30


def test_expected_price_positive():
    assert compute_expected_price(60, 3, MOCK_MODEL) > 0


def test_market_score_fair():
    score, label, ratio = compute_market_score(300_000, 300_000, sigma=0.3)
    assert label == "fair"
    assert ratio == 1.0
    assert score == 1.0


def test_market_score_underpriced():
    _, label, _ = compute_market_score(200_000, 300_000, sigma=0.3)
    assert label == "underpriced"


def test_market_score_overpriced():
    _, label, _ = compute_market_score(400_000, 300_000, sigma=0.3)
    assert label == "overpriced"


def test_distance_score_bounds():
    assert compute_distance_score(0.0) == 1.0
    assert compute_distance_score(10.0) == 0.0
    assert compute_distance_score(15.0) == 0.0
