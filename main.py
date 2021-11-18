from typing import Any, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

import apis.amazon

app = FastAPI()

class Item(BaseModel):
    class HistoryEntry(BaseModel):
        timestamp: float
        price: float
        growth: float
    name: str
    price: float
    description: Optional[str] = None
    platform: str
    url: str
    image: Optional[str] = None
    history: List[HistoryEntry]

dummy_data = [{"name": "XYZ",
             "price": 1234,
             "description": "XYZ",
             "platform": "XYZ",
             "url": "XY.de",
             "image": "https://via.placeholder.com/150",
             "history": [
                 {
                     "timestamp": 1234,
                     "growth": 1,
                     "price": 1234
                 }
             ]}]

@app.get("/", response_model=List[Item])
def query(query: Optional[str] = None, load_new: Optional[bool] = False):
    amazon = apis.amazon.get_items_by_search(query)
    if amazon:
        amazon = add_history_to_items(amazon)
    return concat([
        dummy_data,
        amazon
    ])

# concat multiple lists
def concat(lists: List[List[Item]]) -> List[Item]:
    result = []
    for l in lists:
        result.extend(l)
    return result

def add_history_to_items(items: List[Any]):
    for item in items:
        item['history'] = [
            {
                "timestamp": item['history_timestamp'],
                "price": item['price'],
                "growth": 0
            }
        ]
    return items