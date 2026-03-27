from fastapi import FastAPI, Query
from app.scoring import score_property

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
    latitude: float = Query(..., description="Latitude of the property"),
    longitude: float = Query(..., description="Longitude of the property")
):
    return score_property(
        price=price,
        surface=surface,
        rooms=rooms,
        latitude=latitude,
        longitude=longitude,
    )
