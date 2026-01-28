from fastapi import FastAPI
from app.scoring import get_item

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return get_item(item_id, q)
