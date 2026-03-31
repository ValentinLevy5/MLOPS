import logging

from fastapi import FastAPI, HTTPException, Query

from app.scoring import score_property

logger = logging.getLogger(__name__)

app = FastAPI(title="Property Scoring API")


@app.get("/")
def read_root():
    return {
        "message": "Property Scoring API is running",
        "docs": "/docs"
    }


@app.get("/score")
def get_score(
    price: float = Query(..., gt=0, description="Property price in euros"),
    surface: float = Query(..., gt=5, description="Surface in m²"),
    rooms: int = Query(..., gt=0, description="Number of rooms"),
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude of the property"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude of the property"),
):
    logger.info("Score request: price=%.0f surface=%.1f rooms=%d", price, surface, rooms)
    try:
        return score_property(
            price=price,
            surface=surface,
            rooms=rooms,
            latitude=latitude,
            longitude=longitude,
        )
    except FileNotFoundError as e:
        logger.error("Model not found: %s", e)
        raise HTTPException(status_code=503, detail="Model not loaded. Run train_model.py first.")
    except ValueError as e:
        logger.error("Invalid input or model data: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error during scoring: %s", e)
        raise HTTPException(status_code=500, detail="Internal scoring error.")
