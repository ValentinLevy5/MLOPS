import json
import logging
import math
from pathlib import Path

logger = logging.getLogger(__name__)

CAMPUS_LAT = 48.709681000891
CAMPUS_LON = 2.163486975321

MODEL_PATH = Path("artifacts/model.json")

_REQUIRED_KEYS = {"intercept", "coef_log_surface", "coef_rooms", "sigma", "n_train"}


def load_model() -> dict:
    if not MODEL_PATH.exists():
        logger.error("Model file not found: %s", MODEL_PATH)
        raise FileNotFoundError(
            "Model file not found. Please run train_model.py first."
        )

    with open(MODEL_PATH, "r", encoding="utf-8") as f:
        model = json.load(f)

    missing = _REQUIRED_KEYS - model.keys()
    if missing:
        raise ValueError(f"Model file is missing keys: {missing}")

    logger.info("Loaded model from %s (n_train=%d)", MODEL_PATH, model["n_train"])
    return model


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def compute_expected_price(surface: float, rooms: int, model: dict) -> float:
    log_price = (
        model["intercept"]
        + model["coef_log_surface"] * math.log(surface)
        + model["coef_rooms"] * rooms
    )
    return math.exp(log_price)


def compute_market_score(price: float, expected_price: float, sigma: float) -> tuple[float, str, float]:
    ratio = price / expected_price

    if sigma <= 0:
        logger.warning("sigma is zero or negative; clamping denominator to 1.0")

    # score in [0,1], best when ratio close to 1
    score = max(0.0, 1.0 - abs(math.log(ratio)) / (2 * sigma if sigma > 0 else 1.0))
    score = min(1.0, score)

    if ratio < 0.9:
        label = "underpriced"
    elif ratio <= 1.1:
        label = "fair"
    else:
        label = "overpriced"

    return score, label, ratio


def compute_distance_score(distance_km: float) -> float:
    # 1.0 at 0 km, linear decay to 0 at 10 km
    score = max(0.0, 1.0 - distance_km / 10.0)
    return min(1.0, score)


def score_property(
    price: float,
    surface: float,
    rooms: int,
    latitude: float,
    longitude: float,
) -> dict:
    model = load_model()

    expected_price = compute_expected_price(surface, rooms, model)
    market_score, label, ratio = compute_market_score(
        price=price,
        expected_price=expected_price,
        sigma=model["sigma"],
    )

    distance_km = haversine_km(latitude, longitude, CAMPUS_LAT, CAMPUS_LON)
    distance_score = compute_distance_score(distance_km)

    final_score = 0.7 * market_score + 0.3 * distance_score

    return {
        "input": {
            "price": round(price, 2),
            "surface": round(surface, 2),
            "rooms": rooms,
            "latitude": latitude,
            "longitude": longitude,
        },
        "expected_price": round(expected_price, 2),
        "price_ratio": round(ratio, 3),
        "market_label": label,
        "market_score": round(market_score, 3),
        "distance_to_campus_km": round(distance_km, 3),
        "distance_score": round(distance_score, 3),
        "final_score": round(final_score, 3),
        "n_train": model["n_train"],
    }
