import requests
import time
import functools
from environs import Env
import re

env = Env()
API_KEY = env('API_KEY_EBAY')
def fetch_api(query):
    url = 'https://svcs.ebay.de/services/search/FindingService/v1?'

    querystring = {
      'OPERATION-NAME': 'findItemsAdvanced',
      'SERVICE-VERSION': '1.0.0',
      'SECURITY-APPNAME': API_KEY,
      'RESPONSE-DATA-FORMAT': 'JSON',
      'REST-PAYLOAD': 'true',
      'paginationInput.entriesPerPage': '10',
      'keywords': query,
      'itemFilter(0).name': 'AvailableTo',
      'itemFilter(0).value': 'DE',
      'itemFilter(1).name': 'Currency',
      'itemFilter(1).value': 'EUR',
      'itemFilter(2).name': 'ListingType',
      'itemFilter(2).value': 'FixedPrice',
      }

    return requests.request('GET', url, params=querystring).json()

#clean up the results
def _clean_up_data(results, timestamp):
    clean_results = []
    for result in results['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
        clean_results.append({
              'name': result['title'][0],
              'price': result['sellingStatus'][0]['currentPrice'][0]['__value__'],
              'url': result['viewItemURL'][0],
              'image': result['galleryURL'][0],
              'platform': 'Ebay',
              'timestamp': timestamp,
        })
    return clean_results

def get_items_by_search(query):
    print(f'Fetching new for ${query}')
    results = fetch_api(query)

    timestamp = time.time()

    if results is None:
        return []
    return _clean_up_data(results, timestamp)

'''
not cached for legal reasons

@functools.cache
def get_items_by_search_cached(query):
    return get_items_by_search(query)
'''
