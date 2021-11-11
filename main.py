from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    class HistoryEntry(BaseModel):
        timestamp: int
        price: float
        growth: float
    name: str
    price: float
    description: Optional[str] = None
    platform: str
    url: str
    image: Optional[str] = None
    history: List[HistoryEntry]

@app.get("/", response_model=List[Item])
def query(query: Optional[str] = None):
    return [{"name": "XYZ",
             "price": 1234,
             "description": "XYZ",
             "platform": "XYZ",
             "link": "XY.de",
             "image": "XYZ.de",
             "history": [
                 {
                     "timestamp": 1234,
                     "growth": 1,
                     "price": 1234
                 }
             ]}]
