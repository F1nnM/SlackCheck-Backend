import requests
import time
import functools
from environs import Env
import re

# Load the API key from environment variables
env = Env()
API_KEY = env('API_KEY_AMAZON')

def fetch_api(query):
    url = 'https://amazon-price1.p.rapidapi.com/search'

    querystring = {'keywords':query,'marketplace':'DE'}

    headers = {
        'x-rapidapi-host': 'amazon-price1.p.rapidapi.com',
        'x-rapidapi-key': API_KEY
        }

    return requests.request('GET', url, headers=headers, params=querystring).json()

#clean up the results
def _clean_up_data(results, timestamp):
    clean_results = []
    for result in results:
        # The amazon API retuns the price as a string, sometimes containing the original price as well e.g. "19,99 € (15,99 €)"
        # We only want the current price, so we use regex to extract it.
        # If something has a price of 0, this usually means it's a movie only available on other platforms, and we are not interested in that.
        price = 0
        price_matches = re.findall('^\d+,\d+', result['price'])
        if price_matches:
            price = float(price_matches[0].replace(',', '.'))
        if price > 0:
            clean_results.append({
                'name': result['title'],
                'price': price,
                'url': result['detailPageURL'],
                'image': result['imageUrl'],
                'platform': 'Amazon',
                'timestamp': timestamp,
            })
    return clean_results

def get_items_by_search(query):
    print(f'Fetching new for: {query}')
    results = fetch_api(query)

    timestamp = time.time()

    if results is None:
        return []
    return _clean_up_data(results, timestamp)

@functools.cache
def get_items_by_search_cached(query):
    return get_items_by_search(query)