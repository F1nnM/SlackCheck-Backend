import requests
import time
import functools
from environs import Env

env = Env()
API_KEY = env('API_KEY_BESTBUY')

def fetch_api(query):
    searchParam = ''

    for q in query.split():
        searchParam += 'search=' + q + '&'

    searchParam = searchParam[:-1]
    url = f'https://api.bestbuy.com/v1/products(' + searchParam + ')'

    querystring = {'format':'json','show':'name,salePrice,shortDescription,url,image,upc', 'apiKey':API_KEY}

    return requests.get(url, params=querystring).json()

#clean up the results
def _clean_up_data(results, timestamp):
    clean_results = []
    for result in results:
        clean_results.append({
            'name': result['name'],
            'price': result['salePrice'],
            'description': result['shortDescription'],
            'url': result['url'],
            'image': result['image'],
            'platform': 'BestBuy',
            'timestamp': timestamp,
        })
    return clean_results

def get_items_by_search(query):
    print(f'Fetching new for ${query}')
    results = fetch_api(query)

    timestamp = time.time()

    if results is None:
        return []
    return _clean_up_data(results['products'], timestamp)

@functools.cache
def get_items_by_search_cached(query):
    return get_items_by_search(query)