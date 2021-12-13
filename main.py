from typing import Any, List, Optional, Set

from fastapi import FastAPI
from pydantic import BaseModel

from copy import deepcopy
import time

import apis.amazon
import apis.bestbuy
import apis.ebay
from utils.history import History

app = FastAPI()

"""
The API returns a list of items, which are represented by this class.
"""
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

history = History()

@app.post('/inject')
def inject(input: List[Item]):
    # read the items and save their history
    for item in input:
        for history_entry in item.history:
            history.add(item.url, history_entry.timestamp, history_entry.price)

    return {'status': 'ok'}

@app.get('/', response_model=List[Item])
def query(query: Optional[str] = None, load_new: Optional[bool] = False):

    # debugging tool. Any query preceeded by a ! will be treated as if load_new is True
    if query[0] == '!':
        load_new = True
        query = query[1:]

    # ebay does not allow storing any data, so it will always be loaded
    ebay = apis.ebay.get_items_by_search(query)

    if load_new:
        amazon = apis.amazon.get_items_by_search(query)
        bestbuy = apis.bestbuy.get_items_by_search(query)
    else:
        # deepcopy is necessary to avoid modifying the cached data
        amazon = deepcopy(apis.amazon.get_items_by_search_cached(query))
        bestbuy = deepcopy(apis.bestbuy.get_items_by_search_cached(query))

    all_items = concat([
        amazon,
        bestbuy,
        ebay
    ])

    for item in all_items:
        if item['platform'] is 'Ebay':
            # Ebay does not allow storing any data, so we don't save it it in the history and set the growth to a default value.
            # The only entry in the history will be the current price.
            item['history'] = [{
                'timestamp': item['timestamp'],
                'price': item['price'],
                'growth': 1
            }]
            item['growth'] = 1
        else: 

            # if we load new data, we definitely have new data for the history.
            # If load_new is false, we might still have new data,
            # if this was the first call ever made for that query and the item doesn't exist in the history yet.
            if load_new or not history.contains(item['url']):
                history.add(item['url'], item['timestamp'], item['price'])
            else:
                # if we don't have new data, because this was a cached call,
                # the price in the cached call might be outdated, if some none-cached calls have been made inbetween the cached calls.
                # To avoid this, we load the price from the last history entry, which is guaranteed to be the most recent one.
                _, item['price'] = history.get(item['url'])[-1]

            acc_growth = 1
            for index, (timestamp, price) in enumerate(history.get(item['url'])):
            
                entry = {
                    'timestamp': timestamp,
                    'price': price,
                    'growth': 1
                }

                if index == 0:
                    # growth doesn't need to be calculated for the first entry and can stay 1
                    # history needs to be initialized 
                    item['history'] = []
                else:
                    # for every other enrty, calculate the growth
                    # history is already initialized
                    current_growth = item['history'][index]['price'] / item['history'][index-1]['price']
                    current_growth = int(current_growth*1000)/1000 # round to 3 decimals
                    entry['growth'] = current_growth

                    # accumulation "formula": take the last change.
                    if current_growth != 1:
                        acc_growth = current_growth

                item['history'].append(entry)

            item['growth'] = acc_growth

    return all_items

# utility concat multiple lists
def concat(lists: List[List[Item]]) -> List[Item]:
    result = []
    for l in lists:
        result.extend(l)
    return result