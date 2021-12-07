from typing import Any, List, Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel

from copy import deepcopy
import time

import apis.amazon
import apis.bestbuy
import apis.ebay
from utils.cache import HistoryCache

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
    growth: float
    history: List[HistoryEntry]


''' dummy_data = [{'name': 'XYZ',
             'price': 1234,
             'description': 'XYZ',
             'platform': 'XYZ',
             'url': 'XY.de',
             'image': 'https://via.placeholder.com/150',
             'growth': 1.2,
             'history': [
                 {
                     'timestamp': 1234,
                     'growth': 1,
                     'price': 1234
                 }
             ]}] '''


history = HistoryCache()
cached_calls = set()


@app.get('/', response_model=List[Item])
def query(query: Optional[str] = None, load_new: Optional[bool] = False):
    if query[0] == '!':
        load_new = True
        query = query[1:]

    ebay = apis.ebay.get_items_by_search(query)

    if load_new:
        amazon = apis.amazon.get_items_by_search(query)
        bestbuy = apis.bestbuy.get_items_by_search(query)
    else:
        amazon = deepcopy(apis.amazon.get_items_by_search_cached(query))
        bestbuy = deepcopy(apis.bestbuy.get_items_by_search_cached(query))

    all_items = concat([
        amazon,
        bestbuy,
        ebay
    ])

    for item in all_items:
        if item['platform'] is 'Ebay':
            item['history'] = [{
                'timestamp': item['timestamp'],
                'price': item['price'],
                'growth': 1
            }]
            item['growth'] = 1
        else: 

            if load_new or not query in cached_calls:
                history.add(item['history_id'], item['timestamp'], item['price'])

            item['history'] = [{
                'timestamp': timestamp,
                'price': price
            } for (timestamp, price) in history.get(item['history_id'])]

            growth = 1

            for index in range(len(item['history'])):
                if index == 0:
                    item['history'][index]['growth'] = 1
                else:
                    current_growth = int((item['history'][index]['price'] / item['history'][index-1]['price'])*1000)/1000
                    item['history'][index]['growth'] = current_growth
                    growth *= current_growth

            item['growth'] = growth

            
    cached_calls.add(query)

    return all_items

# concat multiple lists


def concat(lists: List[List[Item]]) -> List[Item]:
    result = []
    for l in lists:
        result.extend(l)
    return result
